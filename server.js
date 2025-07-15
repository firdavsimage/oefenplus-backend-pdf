const express = require('express');
const multer = require('multer');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const app = express();
const PORT = process.env.PORT || 3000;

const uploadDir = path.join(__dirname, 'uploads');
const outputDir = path.join(__dirname, 'converted');

[uploadDir, outputDir].forEach(dir => {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir);
});

const storage = multer.diskStorage({
  destination: uploadDir,
  filename: (req, file, cb) => {
    cb(null, Date.now() + '-' + file.originalname);
  }
});
const upload = multer({ storage });

app.use(express.static('public'));

app.post('/convert', upload.single('file'), (req, res) => {
  const inputPath = req.file.path;
  const ext = path.extname(req.file.originalname).toLowerCase();
  const outputFile = path.join(outputDir, `${Date.now()}.pdf`);

  const cleanup = () => fs.existsSync(inputPath) && fs.unlinkSync(inputPath);

  const sendPDF = () => {
    res.download(outputFile, 'converted.pdf', () => {
      cleanup();
      fs.unlinkSync(outputFile);
    });
  };

  if (['.jpg', '.jpeg', '.png', '.bmp', '.tiff'].includes(ext)) {
    // ImageMagick required
    exec(`convert "${inputPath}" "${outputFile}"`, (err) => {
      if (err) return res.status(500).send('Image PDFga o‘girilmadi');
      sendPDF();
    });
  } else if (['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'].includes(ext)) {
    // LibreOffice is required
    exec(`libreoffice --headless --convert-to pdf "${inputPath}" --outdir "${outputDir}"`, (err) => {
      if (err) return res.status(500).send('Faylni PDFga o‘tkazib bo‘lmadi');
      const converted = inputPath.replace(uploadDir, outputDir).replace(ext, '.pdf');
      res.download(converted, 'converted.pdf', () => {
        cleanup();
        fs.unlinkSync(converted);
      });
    });
  } else {
    cleanup();
    return res.status(400).send('Fayl turi qo‘llab-quvvatlanmaydi');
  }
});

app.listen(PORT, () => {
  console.log(`✅ Server ishga tushdi: http://localhost:${PORT}`);
});
