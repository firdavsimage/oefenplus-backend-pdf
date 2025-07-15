const express = require("express");
const multer = require("multer");
const path = require("path");
const fs = require("fs");
const imageToPdf = require("image-to-pdf");
const cors = require("cors");
const { v4: uuidv4 } = require("uuid");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());

const uploadDir = path.join(__dirname, "uploads");
const outputDir = path.join(__dirname, "converted");

if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir);
if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir);

// Fayl yuklash sozlamalari
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, uploadDir),
  filename: (req, file, cb) => cb(null, uuidv4() + path.extname(file.originalname))
});

const fileFilter = (req, file, cb) => {
  const ext = path.extname(file.originalname).toLowerCase();
  if ([".jpg", ".jpeg", ".png"].includes(ext)) cb(null, true);
  else cb(new Error("Faqat JPG yoki PNG ruxsat etiladi"), false);
};

const upload = multer({ storage, fileFilter });

// POST /convert
app.post("/convert", upload.array("files"), async (req, res) => {
  const files = req.files;
  if (!files || files.length === 0) {
    return res.status(400).json({ error: "Fayl yuborilmadi." });
  }

  const outputFilePath = path.join(outputDir, `${uuidv4()}.pdf`);
  const imagePaths = files.map(f => f.path);

  try {
    const output = fs.createWriteStream(outputFilePath);
    imageToPdf(imagePaths, 'A4').pipe(output);

    output.on("finish", () => {
      res.download(outputFilePath, () => {
        // vaqtincha fayllarni o'chirish (ixtiyoriy)
        imagePaths.forEach(p => fs.unlinkSync(p));
        fs.unlinkSync(outputFilePath);
      });
    });

    output.on("error", (err) => {
      res.status(500).json({ error: "PDF yaratishda xatolik." });
    });

  } catch (err) {
    res.status(500).json({ error: "Server xatoligi." });
  }
});

// Run server
app.listen(PORT, () => {
  console.log(`✅ Server ishga tushdi: http://localhost:${PORT}`);
});

