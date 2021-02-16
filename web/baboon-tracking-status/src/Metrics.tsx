import React from 'react';
import { Line } from 'react-chartjs-2';
import firebase from 'firebase';

interface IState {
    averageErrorRate?: number;
    errorRateCSV?: string;
    errorRateData?: {};
    learningData?: {};
    learningCSV?: {};
}

class Metrics extends React.Component<{}, IState> {
    constructor(props: {}) {
        super(props);

        this.state = {
            errorRateData: {},
            learningData: {}
        };
    }

    getFirebaseDatabase() {
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

        return firebase.database();
    }

    async getChartData() {
        const database = this.getFirebaseDatabase();

        const metricsRef = database.ref("metrics")
        const inputRef = metricsRef.child("input");
        const latestRef = inputRef.child("latest");
        const latestMetricRef = inputRef.child((await latestRef.get()).val());

        const metrics: any[] = (await latestMetricRef.get()).val()

        const chartData = metrics.map((m, idx) => {
            const totalBaboons = m.true_positive + m.false_negative;
            const totalError = m.false_negative + m.false_positive;

            return {
                x: idx / 30,
                y: totalError / totalBaboons
            };
        });

        const csv = btoa(["Frame, True Positive, False Negative, False Positive"]
            .concat(metrics.map((m, idx) => `${idx}, ${m.true_positive}, ${m.false_negative}, ${m.false_positive}`))
            .join("\n"));

        const averageErrorRate = Math.round(chartData.map(x => x.y).reduce((a, b) => a + b) * 10000 / chartData.length) / 100;

        return {
            data: chartData,
            csv: csv,
            averageErrorRate: averageErrorRate
        }
    }

    async getLearningData() {
        const database = this.getFirebaseDatabase();

        const optimizeRef = database.ref("optimize");
        const inputRef = optimizeRef.child("input");
        const lossesRef = inputRef.child("losses");

        const losses = (await lossesRef.get()).val();

        const data = Object.entries(losses).map((l, idx) => {
            const [, value] = l;

            return {
                x: idx + 1,
                y: value
            };
        });

        const csv = btoa(["Iteration, Loss"]
            .concat(data.map(d => `${d.x}, ${d.y}`))
            .join("\n"));

        return {
            csv: csv,
            data: data
        };
    }

    async componentDidMount() {
        const chartData = await this.getChartData();
        const learningData = await this.getLearningData();

        this.setState({
            averageErrorRate: chartData.averageErrorRate,
            errorRateCSV: chartData.csv,
            errorRateData: {
                datasets: [{
                    label: 'Error Rate',
                    data: chartData.data,
                    pointRadius: 0
                }],
            },
            learningData: {
                datasets: [{
                    label: 'Loss',
                    data: learningData.data
                }],
            },
            learningCSV: learningData.csv
        });
    }

    render() {
        return (
            <div>
                <Line data={this.state.errorRateData} options={{
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
                <a download='ErrorRate.csv' href={`data:text/csv;base64,${this.state.errorRateCSV}`}>Download CSV</a>

                <Line data={this.state.learningData} options={{
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: "Loss vs. Iterations"
                    },
                    scales: {
                        xAxes: [{
                            type: 'linear',
                            scaleLabel: {
                                display: true,
                                labelString: "Iterations"
                            }
                        }],
                        yAxes: [{
                            type: 'linear',
                            scaleLabel: {
                                display: true,
                                labelString: "Loss"
                            }
                        }]
                    }
                }} />
                <a download='Learning.csv' href={`data:text/csv;base64,${this.state.learningCSV}`}>Download CSV</a>
            </div>
        );
    }
}

export default Metrics;
