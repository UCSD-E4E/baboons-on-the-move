#include "cv_specializations.h"
#include "sortable_frame.h"

#include "opencv2/core/types.hpp"

#include <tuple>
#include <vector>
#include <assert.h>

namespace baboon_tracking {

template <typename frame> class keypoint_descriptor_container {
  using cvs = cv_specializations<frame>;
  typedef std::tuple <std::vector<cv::KeyPoint>, typename cvs::cpu_or_gpu_mat> memo_entry;
public:
  keypoint_descriptor_container(std::uint8_t max_historical_frames) : max_frames{max_historical_frames} {};
  

  memo_entry& get_keypoint_descriptor(const std::uint64_t frame_num){
    // out of bounds access
    if(mkd.size()==0 || frame_num > std::get<0>(mkd.back())){
      if(mkd.size()==max_frames){
        mkd.erase(mkd.begin());
      }
      std::vector<cv::KeyPoint> kps;
      typename cvs::cpu_or_gpu_mat desc;
      memo_entry memo = std::make_tuple(std::move(kps),std::move(desc));
      mkd.push_back(std::make_tuple(frame_num, std::move(memo)));
      return std::get<1>(mkd.at(mkd.size()-1));
    }
    else if(std::get<0>(mkd.back())-frame_num >= mkd.size()){
      std::vector<cv::KeyPoint> kps;
      typename cvs::cpu_or_gpu_mat desc;
      memo_entry memo = std::make_tuple(std::move(kps),std::move(desc));
      mkd.insert(mkd.begin(), 1, std::make_tuple(frame_num, std::move(memo)));
      return std::get<1>(mkd.front());
    }
    else{
      int ind = std::get<0>(mkd.front());
      return std::get<1>(mkd.at(frame_num-ind));
    }
  }

  bool is_mapped(const std::uint64_t frame_num){
    if(mkd.size()==0){return false;}
    return (frame_num <= std::get<0>(mkd.back()) && frame_num >= std::get<0>(mkd.front()));
  }

private:
  // store the keypoint/descriptors as a vector of tuples.
  // each tuple has the frame num and associated keypoints
  // and descriptors.
  std::vector<std::tuple<std::uint64_t, memo_entry > > mkd;
  // should only need to memoize as many kp/desc as there are
  // historical frames
  std::uint8_t max_frames;
};
}
/*
  void add_keypoint_descriptor_memo(const std::uint64_t frame_num,
                                    const std::vector<cv::KeyPoint> & kp,
                                    const typename cvs::cpu_or_gpu_mat & desc){
    memo_entry memo (frame_num, kp, desc);
    if(mkd.size() == max_frames){
      mkd.erase(mkd.begin());
    }
    mkd.push_back(memo);
  }
  */