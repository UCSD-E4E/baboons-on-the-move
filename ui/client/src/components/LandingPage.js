import React from 'react';
import Grid from '@mui/material/Grid';
import {Link} from 'react-router-dom';

const LandingPage = () => {
  return (
    <div>
      <div style={{paddingBottom: "10vh", paddingTop: "5vh"}}>
        <h1>
          Baboons on the Move
        </h1>
      </div>

      <Grid container spacing={4}>
        <Grid item xs={12}>
          <h2>
            Start
          </h2>
        </Grid>
        <Grid item xs={12}>
          <h4>
            <Link to='/open'>Open Video</Link>
          </h4>
        </Grid>
        <Grid item xs={12}>
          <h4>
            <Link to="/projects">Open Project</Link>
          </h4>
        </Grid>
      </Grid>

    </div>
  )
}

export default LandingPage;
