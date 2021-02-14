import React from 'react';
import './App.css';
import { Line } from 'react-chartjs-2';
import firebase from 'firebase';

interface IState {
  data?: {};
}

class App extends React.Component<{}, IState> {
  constructor(props: {}) {
    super(props);

    this.state = { data: {} };
  }

  async componentDidMount() {
    var config = {
      apiKey: "AIzaSyB83cPhCkA-xv-K6UOZAc0zuH7sxDuxHlE",
      authDomain: "baboon-cli-1598770091002.firebaseapp.com",
      databaseURL: "https://baboon-cli-1598770091002-default-rtdb.firebaseio.com/",
    };

    if (!firebase.apps.length) {
      firebase.initializeApp(config);
    } else {
      firebase.app();
    }

    let database = firebase.database();
    let inputRef = database.ref("metrics/input");
    let latestRef = inputRef.child("latest");
    let latestMetricRef = inputRef.child((await latestRef.get()).val());

    let metrics: any[] = (await latestMetricRef.get()).val()

    let chartData = metrics.map((m, idx) => {
      let totalBaboons = m.true_positive + m.false_negative;
      let totalError = m.false_negative + m.false_positive;

      return {
        x: idx / 30,
        y: totalError / totalBaboons
      };
    });

    this.setState({
      data: {
        datasets: [{
          label: 'Error Rate',
          data: chartData,
          pointRadius: 0
        }],
      }
    });
  }

  render() {
    return (
      <div>
        {/* <h1>Baboons on the Move Status</h1> */}

        <Line data={this.state.data} options={{
          legend: {
            display: false
          },
          title: {
            display: true,
            text: "Error Rate vs. Seconds"
          },
          scales: {
            xAxes: [{
              type: 'linear',
              scaleLabel: {
                display: true,
                labelString: "Seconds"
              }
            }],
            yAxes: [{
              type: 'linear',
              ticks: {
                // Include a dollar sign in the ticks
                callback: function (value: number, index: number, values: number[]) {
                  return Math.round(value * 100) + '%';
                }
              },
              scaleLabel: {
                display: true,
                labelString: "Error Rate"
              }
            }]
          }
        }} />
      </div>
    );
  }
}

export default App;
