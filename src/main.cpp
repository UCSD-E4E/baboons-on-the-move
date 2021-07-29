#include <chrono>
#include <cstdlib>
#include <string>
#include <tuple>

#include <fmt/core.h>

#include <opencv2/imgcodecs.hpp>
#include <opencv2/videoio.hpp>

#include "pipeline.h"
#include "pipes.h"

using baboon_tracking::frame;

struct A {
  frame run(frame &&pass) const { return std::move(pass); }
};

struct B {
  frame run(frame &&pass) const { return std::move(pass); }
  bool should_break() const {
    fmt::print("Got called\n");
    return true;
  }
};

struct C {
  frame run(frame &&pass) {
    fmt::print("poopfard\n");
    return std::move(pass);
  }
};

int main() {
  /*baboon_tracking::pipeline foo{A{}, B{}, C{}};
  fmt::print("Result: {}\n", foo.process(frame{3, cv::Mat{}}).number);*/

  auto hist_frames =
      std::make_shared<baboon_tracking::historical_frames_container>(100);
  baboon_tracking::pipeline pl{
      baboon_tracking::convert_bgr_to_gray{}, baboon_tracking::blur_gray{3},
      baboon_tracking::compute_homography{0.7, 0.2, 0.1, 10000, hist_frames},
      baboon_tracking::transform_history_frames_and_masks{hist_frames}
  };

  // cv::VideoCapture vc{"./sample_1920x1080.avi"};
  cv::Mat image = cv::imread("./maxresdefault.jpg");
  for (std::uint64_t i = 0; /*vc.read(image)*/; i++) {
    auto start = std::chrono::steady_clock::now();
    baboon_tracking::frame fr{i, image.clone()};
    pl.process(std::move(fr));
    auto end = std::chrono::steady_clock::now();

    /*if (res.size() > 0) {
      std::string res_contents = "Result: ";
      res_contents << res[0];

      fmt::print("{}; a {}x{} cv::Mat\n", res_contents, res[0].rows,
                 res[1].cols);
    }*/
    fmt::print(
        "Took {} ms\n",
        std::chrono::duration_cast<std::chrono::milliseconds>(end - start)
            .count());
  }

  return EXIT_SUCCESS;
}
