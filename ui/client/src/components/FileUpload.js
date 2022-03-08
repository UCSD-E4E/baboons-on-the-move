import React, {Fragment, useState} from 'react'
import Message from './Message'
import Progress from './Progress'
import {Link} from 'react-router-dom';
import axios from 'axios';

const FileUpload = () => {
  const [file, setFile] = useState('');
  const [uploadedFile, setUploadedFile] = useState(null);
  const [message, setMessage] = useState('');
  const [uploadPercentage, setUploadPercentage] = useState(0);

  const onChange = e => {
    setFile(e.target.files[0]);
  };

  const onSubmit = async e => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('file', file);

    // Testing Flask connection
    // axios.get('/home')
    //   .then(function (response) {
    //     // handle success
    //     console.log(response);
    //     const data = response.data;
    //     console.log(data);
    //   })
    //   .catch(function (error) {
    //     // handle error
    //     console.log(error);
    //   })
    //   .then(function () {
    //   });

    try {
      const res = await axios.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: progressEvent => {
          setUploadPercentage(parseInt(Math.round(progressEvent.loaded * 100 / progressEvent.total)));
          // Clear percentage after 10 seconds
          setTimeout(() => setUploadPercentage(0), 10000);
        }
      });

      const {fileName, filePath} = res.data;
      setUploadedFile({ fileName, filePath });
      setMessage('File Uploaded');
    } catch(err) {
      if(err.response.status === 500) {
        setMessage('There was a problem with the server');
      }
      else {
        setMessage(err.response.data.msg);
      }
    }
  }

  return (
    <Fragment>
      {message ? <Message msg={message} /> : null}
      <form onSubmit={onSubmit} style={{paddingTop: "5vh"}}>
        <div className="custom-file mb-4">
          <input type="file" className='custom-file-input' id='customFile' onChange={onChange}/>
        </div>

        <Progress percentage={uploadPercentage} />

        <input type="submit" value="Upload" className="btn btn-primary btn-block mt-4" />

      </form>
      
      {uploadedFile ? 
        <div className="row mt-5">
          <h3 className="text-center">
            <Link 
              to="/video" 
              state={{path: uploadedFile.filePath}}>
                Open Video {uploadedFile.fileName}
            </Link>
          </h3>
        </div> : null}
    </Fragment>
  )
}

export default FileUpload;