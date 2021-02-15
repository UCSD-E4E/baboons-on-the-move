import React from 'react';
import { Line } from 'react-chartjs-2';
import firebase from 'firebase';

interface IState {
    averageErrorRate?: number;
    csv?: string;
    data?: {};
}

class Metrics extends React.Component<{}, IState> {
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

        let csv = btoa([", True Positive, False Negative, False Positive"]
            .concat(metrics.map((m, idx) => `${idx}, ${m.true_positive}, ${m.false_negative}, ${m.false_positive}`))
            .join("\n"));

        let averageErrorRate = Math.round(chartData.map(x => x.y).reduce((a, b) => a + b) * 10000 / chartData.length) / 100;

        this.setState({
            averageErrorRate: averageErrorRate,
            csv: csv,
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

                <p>Average Error Rate: {this.state.averageErrorRate}%</p>
                <a download='Data.csv' href={`data:text/csv;base64,${this.state.csv}`}>Download CSV</a>
            </div>
        );
    }
}

export default Metrics;
