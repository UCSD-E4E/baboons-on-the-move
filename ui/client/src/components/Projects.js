import React from 'react';
import {Link} from 'react-router-dom';

const Projects = () => {
  function importAll(r) {
    let videos = {};
    r.keys().forEach(item => {
      videos[item.replace('./', '')] = r(item);
    });
    return videos;
  }
  const videos = importAll(require.context('../../public/uploads', false, /\.(mp4)$/));

  return (
    <div>
      <h2>
        Projects
      </h2>

      {videos ? 
        Object.keys(videos).map((video) => (
          <h3 key={video}>
            <Link to="/video" state={{path: videos[video]}}>
                {video}
            </Link>
          </h3>
        )) : null}
    </div>
  )
}

export default Projects;
