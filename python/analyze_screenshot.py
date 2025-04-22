import cv2
from solve import *
from rich import print

def analyze_screenshot(image):
    # crop to grid
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour_largest = sorted(contours, key=cv2.contourArea)[-1]
    x, y, w, h = cv2.boundingRect(contour_largest)
    cropped = image[y:y+h, x:x+w]
    cropped = cv2.resize(cropped, (600, int(600 * h / w)))

    # grid detection
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)[1]
    sobelx = cv2.Sobel(thresh, cv2.CV_64F, 1, 0, ksize=5)
    sobelx = cv2.convertScaleAbs(cv2.max(sobelx, 0))
    cv2.imshow("Sobel", sobelx)

    # hough lines
    lines = cv2.HoughLinesP(sobelx, 1, 3 / 180, threshold=100, minLineLength=100, maxLineGap=10)
    x_pos = [line[0][0] for line in lines]
    x_pos.sort()
    dist = 0
    num_lines = 0
    for i in range(len(x_pos) - 1):
        if x_pos[i + 1] - x_pos[i] > 10:
            dist += x_pos[i + 1] - x_pos[i]
            num_lines += 1
    dist /= num_lines
    grid_size = round(600 / dist)
    print("Grid size:", grid_size)

    # sample
    points = []
    #cropped = cv2.bitwise_and(cropped, cropped, mask=thresh)
    dist = 600 // grid_size
    for i in range(grid_size):
        for j in range(round(grid_size * h / w)):
            x = int(i * dist + dist / 2)
            y = int(j * dist + dist / 2)
            if cropped[y, x][0] > 50 or cropped[y, x][1] > 50 or cropped[y, x][2] > 50:
                points.append((j, i, tuple(cropped[y,x])))
                cv2.drawMarker(cropped, (x, y), (0, 0, 255), cv2.MARKER_CROSS, 10, 2)
    print(len(points), "points found")
   
    # match endpoints
    endpoints = []
    for i in range(len(points)):
        best = None
        best_dist = 100
        for j in range(i):
            print(points[i][2], points[j][2])
            d = int(int(points[i][2][0]) - int(points[j][2][0])) ** 2 + \
                int(int(points[i][2][1]) - int(points[j][2][1])) ** 2 + \
                int(int(points[i][2][2]) - int(points[j][2][2])) ** 2
            
            if d < best_dist:
                best_dist = d
                best = points[j][0:2]
                print(points[i][2], points[j][2], d)
        if best is not None:
            endpoints.append([points[i][0:2], best, len(endpoints)])
            cv2.line(cropped, (
                    int(points[i][1] * dist + dist / 2),
                    int(points[i][0] * dist + dist / 2)
                ),
                (
                    int(best[1] * dist + dist / 2),
                    int(best[0] * dist + dist / 2)
                ),
                (255, 0, 0),
                2
            )
        else:
            print("No best found for", points[i])
    cv2.imshow("Endpoints", cropped)
    print("Endpoints:", endpoints)
    cv2.waitKey(0)
    return endpoints, round(grid_size * h / w), grid_size

if __name__ == "__main__":
    img = cv2.imread("screenshot.jpg")
    endpoints, n, m = analyze_screenshot(img)
    puzzle = build(endpoints, n, m)

    clear()
    render(puzzle)
    solve(puzzle, endpoints)