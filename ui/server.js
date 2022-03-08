const express = require('express');
const fileUpload = require('express-fileupload');

const app = express();
app.use(fileUpload());

app.post('/upload', (req, res) => {
  if(req.files === null) {
    return res.status(400).json({ msg: 'No file upload' });
  }

  const file = req.files.file;

  file.mv(`${__dirname}/client/public/uploads/${file.name}`, err => {
    if (err) {
      console.error(err);
      return res.status(500).send(err);
    }

    res.json({ fileName: file.name, filePath: `/uploads/${file.name}` });
  })
})

const request = require('request');
app.get('/home', (req, res) => {
    request('http://127.0.0.1:7000/flask', function (error, response, body) {
        console.error('error:', error); 
        console.log('statusCode:', response && response.statusCode);
        console.log('body:', body); 
        res.send(body);
      });      
});

app.listen(5000, () => console.log('Server Stared...'));
