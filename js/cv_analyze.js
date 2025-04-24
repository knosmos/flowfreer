document.getElementById('imgInput').addEventListener('change', function (e) {
    let file = e.target.files[0];
    let img = new Image();
    img.onload = () => {
        // load image into canvas for opencv processing
        let canvas = document.getElementById('canvasOutput');
        canvas.width = img.width;
        canvas.height = img.height;
        let ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0);
        let src = cv.imread(canvas);

        let analysis = analyzeScreenshot(src);
        console.log("Endpoints:", analysis.endpoints);
        console.log("Grid size:", analysis.n, analysis.m);

        // set puzzle data
        resetBoard();
        table.puzzle = build(analysis.endpoints, analysis.n, analysis.m);
        table.original = structuredClone(table.puzzle);
        table.endpoints = analysis.endpoints;
        table.n = analysis.n;
        table.m = analysis.m;
        table.num_placed = analysis.endpoints.length * 2;
        src.delete();
    };
    img.src = URL.createObjectURL(file);
});

function analyzeScreenshot(image) {
    // crop to main grid
    let gray = new cv.Mat();
    cv.cvtColor(image, gray, cv.COLOR_RGBA2GRAY);

    let edges = new cv.Mat();
    cv.Canny(gray, edges, 50, 150);

    let contours = new cv.MatVector();
    let hierarchy = new cv.Mat();
    cv.findContours(edges, contours, hierarchy, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE);

    let largest = contours.get(0);
    for (let i = 1; i < contours.size(); i++) {
        if (cv.contourArea(contours.get(i)) > cv.contourArea(largest)) {
            largest = contours.get(i);
        }
    }

    let rect = cv.boundingRect(largest);
    let cropped = image.roi(rect);
    let aspectRatio = cropped.rows / cropped.cols;
    cv.resize(cropped, cropped, new cv.Size(600, parseInt(600 * aspectRatio)));

    // detect vertical grid lines
    let croppedGray = new cv.Mat();
    cv.cvtColor(cropped, croppedGray, cv.COLOR_RGBA2GRAY);
    let thresh = new cv.Mat();
    cv.threshold(croppedGray, thresh, 0, 255, cv.THRESH_OTSU);

    let sobelX = new cv.Mat();
    cv.Sobel(thresh, sobelX, cv.CV_64F, 1, 0, 5);
    sobelX.convertTo(sobelX, cv.CV_8U);

    let lines = new cv.Mat();
    cv.HoughLinesP(sobelX, lines, 1, Math.PI / 60, 100, 100, 10);

    // calculate grid size
    let xPos = [];
    for (let i = 0; i < lines.rows; i++) {
        let pt = lines.intPtr(i);
        xPos.push(pt[0]);
    }
    xPos.sort((a, b) => a - b);

    let dist = 0, numLines = 0;
    for (let i = 0; i < xPos.length - 1; i++) {
        if (xPos[i + 1] - xPos[i] > 10) {
            dist += xPos[i + 1] - xPos[i];
            numLines++;
        }
    }
    dist /= numLines;
    let gridSize = Math.round(600 / dist);
    console.log("Grid size:", gridSize);

    // detect color points
    let points = [];
    let step = 600 / gridSize;
    for (let i = 0; i < gridSize; i++) {
        for (let j = 0; j < Math.round(gridSize * aspectRatio); j++) {
            let x = Math.round(i * step + step / 2);
            let y = Math.round(j * step + step / 2);
            let px = cropped.ucharPtr(y, x);
            if (px[0] > 50 || px[1] > 50 || px[2] > 50) {
                points.push([j, i, [px[0], px[1], px[2]]]);
            }
        }
    }
    console.log(points.length + " points found");

    // matchmaker
    let endpoints = [];
    for (let i = 0; i < points.length; i++) {
        let best = null;
        let bestDist = 100;
        for (let j = 0; j < i; j++) {
            let c1 = points[i][2];
            let c2 = points[j][2];
            let d = (c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2;
            if (d < bestDist) {
                bestDist = d;
                best = points[j].slice(0, 2);
            }
        }
        if (best) {
            endpoints.push([points[i].slice(0, 2), best, endpoints.length]);
            let pt1 = new cv.Point(points[i][1] * step + step / 2, points[i][0] * step + step / 2);
            let pt2 = new cv.Point(best[1] * step + step / 2, best[0] * step + step / 2);
            cv.line(cropped, pt1, pt2, new cv.Scalar(255, 0, 0), 2);
        } else {
            console.log("No best match found for", points[i]);
        }
    }

    console.log("Endpoints:", endpoints);
    cv.imshow("canvasOutput", cropped);

    // Clean up
    gray.delete(); edges.delete(); contours.delete(); hierarchy.delete();
    croppedGray.delete(); thresh.delete(); sobelX.delete(); lines.delete();

    return {endpoints, n: Math.round(gridSize * aspectRatio), m: gridSize};
}