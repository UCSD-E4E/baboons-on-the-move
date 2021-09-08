#pragma once

#include "sortable_frame.h"

#include <condition_variable>
#include <mutex>
#include <set>

namespace baboon_tracking {
template <typename frame> class historical_frames_container {
private:
  using frame_set_t = std::set<sortable_frame<frame>, std::less<>>;

public:
  historical_frames_container(
      typename frame_set_t::size_type max_historical_frames,
      unsigned int max_concurrency)
      : max_frames{max_historical_frames}, max_concurrency{max_concurrency} {};

  void add_historical_frame(std::uint64_t frame_num,
                            frame &&preprocessed_frame) {
    {
      std::scoped_lock lk{mutex};
      // This is just greater than because we assume the caller adds a frame
      // before accessing it
      if (historical_frames.size() > max_frames + max_concurrency) {
        historical_frames.erase(historical_frames.begin());
      }
      historical_frames.emplace(
          sortable_frame<frame>{frame_num, std::move(preprocessed_frame)});
    }

    frame_added_cv.notify_all();
  }

  // If the numbered frame is not yet available this will block until that frame
  // is added Why do we copy frame here and nowhere else? In other cases it's
  // easy to just move frame and better indicates intent, but in this case
  // returning a reference to frame would require holding the lock for the
  // duration of its use because it's possible that the frame gets removed from
  // the set when another thread adds a frame and old frames get cleaned up.
  // Copying the frame does *not* cause a copy of the frame's cv::Mat's
  // underlying data, because cv::Mat is effectively a std::shared_ptr (it does
  // reference counting.)
  frame get_historical_frame(std::uint64_t frame_number) {
    std::unique_lock lk{mutex};

    if (!historical_frames.count(frame_number)) {
      frame_added_cv.wait(
          lk, [&historical_frames = historical_frames, frame_number]() {
            return historical_frames.count(frame_number);
          });
    }

    auto sortable_frame = historical_frames.find(frame_number);
    return sortable_frame->frame;
  }

  bool is_full() {
    std::unique_lock lk{mutex};
    return historical_frames.size() >= max_frames;
  }

  typename frame_set_t::size_type max_historical_frames() const {
    return max_frames;
  }

private:
  std::mutex mutex;
  std::condition_variable frame_added_cv;

  frame_set_t historical_frames;
  typename frame_set_t::size_type max_frames;
  unsigned int max_concurrency;
};
} // namespace baboon_tracking
