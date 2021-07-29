#pragma once

#include <functional>
#include <string>
#include <tuple>
#include <utility>

#include <fmt/core.h>

namespace baboon_tracking {
template <typename... Pipes> class pipeline {
private:
  template <typename> struct is_tuple : std::false_type {};
  template <typename... Ts>
  struct is_tuple<std::tuple<Ts...>> : std::true_type {};

  // These take a long and int parameter to break overload ambiguity when the
  // only thing constraining the overload resolution is the expression SFINAE
  template <typename T>
  auto should_break_impl(T &pipe, int) -> decltype(pipe.should_break()) {
    return pipe.should_break();
  }
  template <typename T>
  auto should_break_impl(T &, long) {
    return false;
  }

  template <typename T> bool should_break(T &pipe) {
    // Default to the first overload (which taks an int) when there is ambiguity
    return should_break_impl(pipe, int{});
  }

private:
  std::tuple<Pipes...> pipes;

  // Base case (we've run all the pipes)
  template <typename I> I run_pipes(I &&input) {
    return std::forward<I>(input);
  }

  // Recursive case for when input is a tuple (need to overload instead of if
  // constexpr because we need to get the tuple's parameter pack to forward
  // correctly)
  template <typename... Is, typename T, typename... Ts>
  auto run_pipes(std::tuple<Is...> &&input, T &first_pipe,
                 Ts &... rest_of_pipes) {
    // Need to use a lambda to proxy the call; std::bind won't work here
    auto first_pipe_run_proxy = [&first_pipe](auto &&... inputs) {
      return first_pipe.run(std::forward<Is>(inputs)...);
    };
    auto &&first_pipe_ret = std::apply(first_pipe_run_proxy,
                                       std::forward<std::tuple<Is...>>(input));

    if (should_break(first_pipe)) {
      std::remove_reference_t<decltype(
          run_pipes(std::forward<decltype(first_pipe_ret)>(first_pipe_ret),
                    rest_of_pipes...))>
          default_constructed_return{};
      return default_constructed_return;
    }

    return run_pipes(std::forward<decltype(first_pipe_ret)>(first_pipe_ret),
                     rest_of_pipes...);
  }

  // Recursive case for when input is not a tuple
  template <typename I, typename T, typename... Ts>
  auto run_pipes(I &&input, T &first_pipe, Ts &... rest_of_pipes) {
    auto &&first_pipe_ret = first_pipe.run(std::forward<I>(input));

    if (should_break(first_pipe)) {
      std::remove_reference_t<decltype(
          run_pipes(std::forward<decltype(first_pipe_ret)>(first_pipe_ret),
                    rest_of_pipes...))>
          default_constructed_return{};
      return default_constructed_return;
    }

    return run_pipes(std::forward<decltype(first_pipe_ret)>(first_pipe_ret),
                     rest_of_pipes...);
  }

public:
  pipeline(Pipes &&... pipes) : pipes{std::tuple(std::move(pipes)...)} {}

  // Note: there is currently no support for the case where the first pipe takes
  // no arguments

  template <typename I> auto process(I &&input) {
    // Need a proxy function because std::apply can't directly apply to a member
    // and std::bind is a pain
    auto run_pipes_proxy = [this, &input](Pipes &... pipes) {
      return run_pipes(std::forward<I>(input), pipes...);
    };
    return std::apply(run_pipes_proxy, pipes);
  }

  template <typename... Is> auto process(Is &&... inputs) {
    return process(std::make_tuple(inputs...));
  }
};
} // namespace baboon_tracking
