/*
MIT License

Copyright (c) 2018 Oleksandr Bailo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

// From
// https://github.com/BAILOOL/ANMS-Codes/blob/fca9463512bb24a0e72bcdc7e36693be557f1fbb/C++/CmakeProject/source/anms.h
// With some stylistic changes

#pragma once

#include <opencv2/features2d.hpp>
#include <vector>

namespace anms {
std::vector<cv::KeyPoint> ssc(const std::vector<cv::KeyPoint> &key_points,
                              int num_ret_points, double tolerance, int cols,
                              int rows) {
  // several temp expression variables to simplify solution equation
  int exp1 = rows + cols + 2 * num_ret_points;
  long long exp2;
  {
    long long rows_ll = static_cast<long long>(rows);
    long long cols_ll = static_cast<long long>(cols);
    long long num_ret_points_ll = static_cast<long long>(num_ret_points);

    exp2 =
        (4 * cols_ll + 4 * num_ret_points_ll + 4 * rows_ll * num_ret_points_ll +
         rows_ll * rows_ll + cols_ll * cols_ll - 2 * rows_ll * cols_ll +
         4 * rows_ll * cols_ll * num_ret_points_ll);
  }
  double exp3 = std::sqrt(exp2);
  double exp4 = num_ret_points - 1;

  double sol1 = -std::round((exp1 + exp3) / exp4); // first solution
  double sol2 = -std::round((exp1 - exp3) / exp4); // second solution

  double high =
      (sol1 > sol2)
          ? sol1
          : sol2; // binary search range initialization with positive solution
  double low = std::floor(
      std::sqrt(static_cast<double>(key_points.size()) / num_ret_points));

  double width;
  double prev_width = -1;

  std::vector<int> result_vec;
  bool complete = false;
  unsigned int K = num_ret_points;
  unsigned int K_min = std::round(K - (K * tolerance));
  unsigned int K_max = std::round(K + (K * tolerance));

  std::vector<int> result;
  result.reserve(key_points.size());
  while (!complete) {
    width = low + (high - low) / 2;
    if (width == prev_width ||
        low >
            high) { // needed to reassure the same radius is not repeated again
      result_vec = result; // return the keypoints from the previous iteration
      break;
    }

    double c = width / 2; // initializing Grid
    int num_cell_cols = std::floor(cols / c);
    int num_cell_rows = std::floor(rows / c);
    std::vector<std::vector<bool>> covered_vec(
        num_cell_rows + 1, std::vector<bool>(num_cell_cols + 1, false));
    result.clear();

    for (unsigned int i = 0; i < key_points.size(); ++i) {
      int row =
          std::floor(key_points[i].pt.y /
                     c); // get position of the cell current point is located at
      int col = std::floor(key_points[i].pt.x / c);
      if (covered_vec[row][col] == false) { // if the cell is not covered
        result.push_back(i);
        int row_min = ((row - std::floor(width / c)) >= 0)
                          ? (row - std::floor(width / c))
                          : 0; // get range which current radius is covering
        int row_max = ((row + std::floor(width / c)) <= num_cell_rows)
                          ? (row + std::floor(width / c))
                          : num_cell_rows;
        int col_min = ((col - std::floor(width / c)) >= 0)
                          ? (col - std::floor(width / c))
                          : 0;
        int col_max = ((col + std::floor(width / c)) <= num_cell_cols)
                          ? (col + std::floor(width / c))
                          : num_cell_cols;
        for (int row_to_cov = row_min; row_to_cov <= row_max; ++row_to_cov) {
          for (int col_to_cov = col_min; col_to_cov <= col_max; ++col_to_cov) {
            if (!covered_vec[row_to_cov][col_to_cov])
              covered_vec[row_to_cov][col_to_cov] =
                  true; // cover cells within the square bounding box with width
                        // w
          }
        }
      }
    }

    if (result.size() >= K_min && result.size() <= K_max) { // solution found
      result_vec = result;
      complete = true;
    } else if (result.size() < K_min)
      high = width - 1; // update binary search range
    else
      low = width + 1;
    prev_width = width;
  }
  // retrieve final keypoints
  std::vector<cv::KeyPoint> kp;
  for (unsigned int i = 0; i < result_vec.size(); i++)
    kp.push_back(key_points[result_vec[i]]);

  return kp;
}
} // namespace anms
