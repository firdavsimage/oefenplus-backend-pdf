const express = require("express");
const cors = require("cors");
const multer = require("multer");
const fs = require("fs");
const path = require("path");
const { v4: uuidv4 } = require("uuid");

const app = express();
const PORT = process.env.PORT || 3000;

// Middlewares
app.use(cors());
app.use(express.json());
app.use("/output", express.static(path.join(__dirname, "output")));

const upload = multer({ dest: "uploads/" });

app.get("/", (req, res) => {
  res.send("PDF Converter backend is running.");
});

// === Image to PDF ===
const sharp = require("sharp");
const { PDFDocument } = require("pdf-lib");

app.post("/convert/image", upload.array("images"), async (req, res) => {
  try {
    const pdfDoc = await PDFDocument.create();

    for (const file of req.files) {
      const imageBuffer = fs.readFileSync(file.path);
      const image = await sharp(imageBuffer).jpeg().toBuffer();
      const img = await pdfDoc.embedJpg(image);
      const page = pdfDoc.addPage([img.width, img.height]);
      page.drawImage(img, { x: 0, y: 0, width: img.width, height: img.height });
    }

    const pdfBytes = await pdfDoc.save();
    const outputPath = `output/${uuidv4()}.pdf`;
    fs.writeFileSync(outputPath, pdfBytes);

    req.files.forEach(file => fs.unlinkSync(file.path)); // delete uploaded files

    res.json({ download: `${req.protocol}://${req.get("host")}/${outputPath}` });
  } catch (error) {
    console.error(error);
    res.status(500).send("Conversion failed");
  }
});

// === Add Word, Excel, PPT conversions here if needed ===

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
