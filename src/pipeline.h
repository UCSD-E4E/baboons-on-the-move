#pragma once

#include <functional>
#include <string>
#include <tuple>
#include <utility>

namespace baboon_tracking {
template <typename... Pipes> class pipeline {
private:
  template <typename... Ts> struct select_last {
    // Can be replaced with std::type_identity in C++20
    template <typename T> struct type_identity { using type = T; };

    // Do a unary right fold expression with the comma operator to get the last
    // type in our parameter pack
    using type = typename decltype((type_identity<Ts>{}, ...))::type;
  };

  // Assumes there's a function on the first and last pipe called run
  using pipeline_result_t = typename decltype(
      std::mem_fn(&select_last<Pipes...>::type::run))::result_type;

  template <typename> struct is_tuple : std::false_type {};
  template <typename... Ts>
  struct is_tuple<std::tuple<Ts...>> : std::true_type {};

private:
  std::tuple<Pipes...> pipes;

  // Base case
  template <typename I> I run_pipes(I &&input) {
    return std::forward<I>(input);
  }

  // Recursive case for when input is a tuple (need to overload instead of if
  // constexpr because we need to get the tuple's parameter pack to forward
  // correctly)
  template <typename... Is, typename T, typename... Ts>
  auto run_pipes(std::tuple<Is...> &&input, const T &first_pipe,
                 const Ts &... rest_of_pipes) {
    auto first_pipe_run = [&first_pipe](auto &&... inputs) {
      return first_pipe.run(std::forward<Is>(inputs)...);
    };
    return run_pipes(
        std::apply(first_pipe_run, std::forward<std::tuple<Is...>>(input)),
        rest_of_pipes...);
  }

  // Recursive case for when input is not a tuple
  template <typename I, typename T, typename... Ts>
  auto run_pipes(I &&input, const T &first_pipe, const Ts &... rest_of_pipes) {
    return run_pipes(first_pipe.run(std::forward<I>(input)), rest_of_pipes...);
  }

public:
  pipeline(Pipes &&... pipes) : pipes{std::make_tuple(std::move(pipes)...)} {}

  template <typename I> pipeline_result_t process(I &&input) {
    // Need a proxy function because std::apply can't directly apply to a member
    // and std::bind is a pain
    auto run_pipes_proxy = [this, &input](const Pipes &... pipes) {
      return run_pipes(std::forward<I>(input), pipes...);
    };
    return std::apply(run_pipes_proxy, pipes);
  }
};
} // namespace baboon_tracking
