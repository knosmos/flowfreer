import cv2
import solve
from rich import print

def analyze_screenshot(image):
    # crop to square
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour_largest = sorted(contours, key=cv2.contourArea)[-1]
    x, y, w, h = cv2.boundingRect(contour_largest)
    cropped = image[y:y+h, x:x+w]
    cropped = cv2.resize(cropped, (600, 600))
    # cv2.imshow("Cropped", cropped)

    # grid detection
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)[1]
    sobelx = cv2.Sobel(thresh, cv2.CV_64F, 1, 0, ksize=5)
    sobelx = cv2.convertScaleAbs(cv2.max(sobelx, 0))
    # cv2.imshow("Threshold", sobelx)
    # hough lines
    lines = cv2.HoughLinesP(sobelx, 1, 3 / 180, threshold=100, minLineLength=100, maxLineGap=10)
    # draw
    # for line in lines:
    #     x1, y1, x2, y2 = line[0]
    #     cv2.line(cropped, (x1, y1), (x2, y2), (0, 255, 0), 2)
    x_pos = [line[0][0] for line in lines]
    x_pos.sort()
    dist = 0
    num_lines = 0
    for i in range(len(x_pos) - 1):
        if x_pos[i + 1] - x_pos[i] > 5:
            dist += x_pos[i + 1] - x_pos[i]
            num_lines += 1
    dist /= num_lines
    grid_size = int(600 / dist)
    print("Grid size:", grid_size)
    # cv2.imshow("Lines", cropped)

    # sample
    points = []
    cropped = cv2.bitwise_and(cropped, cropped, mask=thresh)
    cv2.imshow("Sampled", cropped)
    dist = 600 // grid_size
    for i in range(grid_size):
        for j in range(grid_size):
            x = int(i * dist + dist / 2)
            y = int(j * dist + dist / 2)
            if cropped[y, x][0] > 10 or cropped[y, x][1] > 10 or cropped[y, x][2] > 10:
                points.append((i, j, tuple(cropped[y,x])))
                cv2.drawMarker(cropped, (x, y), (0, 0, 255), cv2.MARKER_CROSS, 10, 2)
    print(len(points), "points found")
    cv2.imshow("Sampled", cropped)
   
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
                    int(points[i][0] * dist + dist / 2),
                    int(points[i][1] * dist + dist / 2)
                ),
                (
                    int(best[0] * dist + dist / 2),
                    int(best[1] * dist + dist / 2)
                ),
                (255, 0, 0),
                2
            )
        else:
            print("No best found for", points[i])
    cv2.imshow("Endpoints", cropped)
    print("Endpoints:", endpoints)
    cv2.waitKey(0)

if __name__ == "__main__":
    img = cv2.imread("screenshot.jpg")
    analyze_screenshot(img)