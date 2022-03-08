import './App.css';
import FileUpload from './components/FileUpload';
import LandingPage from './components/LandingPage';
import Projects from './components/Projects';
import Video from './components/Video';
import {Routes, Route} from 'react-router-dom';

const App = () => {
  return (
    <div className="App">
      <Routes>
        <Route exact path="/" element={<LandingPage/>} />
        <Route exact path="/open" element={<FileUpload/>} />
        <Route exact path="/projects" element={<Projects/>} />
        <Route exact path="/video" element={<Video/>} />
      </Routes>
    </div>
  );
}

export default App;
