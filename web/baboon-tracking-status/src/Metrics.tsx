import React from 'react';
import { Line } from 'react-chartjs-2';
import firebase from 'firebase';

interface IState {
    errorRateLastUpdated?: number;
    averageErrorRate?: number;
    errorRateCSV?: string;
    errorRateData?: {};
    learningData?: {};
    learningCSV?: {};
    learningPercentImprovement?: number;
    learningLatestUpdate?: number;
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

    private parseDate(dateString: string): number {
        const [datePart, timePart] = dateString.split('-');
        const year = parseInt(datePart.substr(0, 4));
        const month = parseInt(datePart.substr(4, 2)) - 1;
        const day = parseInt(datePart.substr(6, 2));

        const hour = parseInt(timePart.substr(0, 2));
        const minute = parseInt(timePart.substr(2, 2));
        const second = parseInt(timePart.substr(4, 2));

        return Date.UTC(year, month, day, hour, minute, second);
    }

    async getChartData() {
        const database = this.getFirebaseDatabase();

        const metricsRef = database.ref("metrics")
        const inputRef = metricsRef.child("input");
        const latestRef = inputRef.child("latest");

        const latest: string = (await latestRef.get()).val();
        const latestMetricRef = inputRef.child(latest);
        const latestUpdate = this.parseDate(latest);

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
            averageErrorRate: averageErrorRate,
            latestUpdate: latestUpdate
        }
    }

    async getLearningData() {
        const database = this.getFirebaseDatabase();

        const optimizeRef = database.ref("optimize");
        const inputRef = optimizeRef.child("input");
        const latestRef = inputRef.child("latest");
        const lossesRef = inputRef.child("losses");
        const latest: string = (await latestRef.get()).val();

        const losses = (await lossesRef.get()).val();

        const [latestUpdateString,] = Object.entries(losses).slice(-1)[0];
        const latestUpdate = this.parseDate(latestUpdateString);

        const data = Object.entries(losses).map((l, idx) => {
            const [, value] = l;

            return {
                x: idx + 1,
                y: value as number
            };
        });

        const dataPointBackgroundColor = Object.entries(losses).map(l => {
            const [key,] = l;

            return key === latest ? "#90cd8a" : "rgba(0, 0, 0, 0.1)";
        })

        let percentImprovement: number = 0;
        if (data.length > 1) {
            const best = Object.entries(losses).filter(l => {
                const [key,] = l;

                return key === latest;
            }).map(l => {
                const [, value] = l;

                return value as number;
            })[0];
            percentImprovement = Math.round((data[0].y - best) * 10000 / data[0].y) / 100;
        }

        const csv = btoa(["Iteration, Loss"]
            .concat(data.map(d => `${d.x}, ${d.y}`))
            .join("\n"));

        return {
            csv: csv,
            data: data,
            percentImprovement: percentImprovement,
            latestUpdate: latestUpdate,
            dataPointBackgroundColor: dataPointBackgroundColor
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
            errorRateLastUpdated: chartData.latestUpdate,
            learningData: {
                datasets: [{
                    label: 'Loss',
                    data: learningData.data,
                    pointBackgroundColor: learningData.dataPointBackgroundColor
                }],
            },
            learningCSV: learningData.csv,
            learningPercentImprovement: learningData.percentImprovement,
            learningLatestUpdate: learningData.latestUpdate
        });
    }

    render() {
        const errorRateLastUpdate = new Date(this.state.errorRateLastUpdated || 0);
        const learningLatestUpdate = new Date(this.state.learningLatestUpdate || 0);

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

                <p>Last Updated: {`${errorRateLastUpdate.toLocaleDateString()} ${errorRateLastUpdate.toLocaleTimeString()}`}</p>
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
                <p>Last Updated: {`${learningLatestUpdate.toLocaleDateString()} ${learningLatestUpdate.toLocaleTimeString()}`}</p>
                <p>Percent Improvement: {this.state.learningPercentImprovement}%</p>
                <a download='Learning.csv' href={`data:text/csv;base64,${this.state.learningCSV}`}>Download CSV</a>
            </div>
        );
    }
}

export default Metrics;
