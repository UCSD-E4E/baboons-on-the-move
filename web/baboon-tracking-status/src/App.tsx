import React from 'react';
import './App.css';
import Metrics from './Metrics';

class App extends React.Component<{}, {}> {
  render() {
    return (
      <div>
        {/* <h1>Baboons on the Move Status</h1> */}

        <Metrics />
      </div>
    );
  }
}

export default App;
