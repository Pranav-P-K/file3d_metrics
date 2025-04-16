const express = require('express');
const multer = require('multer');
const cors = require('cors');
const fs = require('fs-extra');
const STL = require('node-stl');
const path = require('path');
const { execFile } = require('child_process');
const { promisify } = require('util');
const execFileAsync = promisify(execFile);

const app = express();
const storage = multer.diskStorage({
    destination: 'uploads/',
    filename: (req, file, cb) => {
        const ext = path.extname(file.originalname).toLowerCase();
        cb(null, file.fieldname + '-' + Date.now() + ext);
    }
});

const upload = multer({ storage: storage });

app.use(cors());
app.use(express.static('public'));

// STL Volume Calculation
function calculateSTLMetrics(filePath) {
    const buffer = fs.readFileSync(filePath);
    const stl = new STL(buffer);
    const volume = stl.volume;
    const surfaceArea = stl.area;
    const meshDensity = stl.facets;
    return { volume, surfaceArea, meshDensity };
}

// STEP Volume Calculation 
async function calculateSTEPMetrics(filePath) {
    try {
        const { stdout, stderr } = await execFileAsync(
            'C:/Program Files/FreeCAD 1.0/bin/python.exe',
            ['C:/Programming/Internship/Quetzalcoatl/StepVol/file3d_metrics/step_vol.py', filePath],
            { timeout: 30000 }
        );

        const [volStr, areaStr, faceCountStr] = stdout.trim().split(',');
        const volume = parseFloat(volStr);
        const surfaceArea = parseFloat(areaStr);
        const meshDensity = parseInt(faceCountStr);
        if (isNaN(volume) || isNaN(surfaceArea) || isNaN(meshDensity)) {
            throw new Error('Invalid output from FreeCAD');
        }
        return { volume, surfaceArea, meshDensity };
    } catch (err) {
        throw new Error(`FreeCAD processing failed: ${err.stderr || err.message}`);
    }
}

// File Upload Handler
app.post('/upload', upload.single('file'), async (req, res) => {
    try {
        let filePath = req.file.path;
        const ext = path.extname(req.file.originalname).toLowerCase();

        if (ext === '.stl') {
            const { volume, surfaceArea, meshDensity } = calculateSTLMetrics(filePath);
            return res.json({
                filename: req.file.originalname,
                volume,
                surfaceArea,
                meshDensity
            });
        } else if (ext === '.step') {
            const { volume, surfaceArea, meshDensity } = await calculateSTEPMetrics(filePath);
            return res.json({
                filename: req.file.originalname,
                volume,
                surfaceArea,
                meshDensity
            });
        } else {
            return res.status(400).json({ error: 'Unsupported file format' });
        }

    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.listen(3000, () => console.log('Server running on http://localhost:3000'));
