#include <cstdlib>
#include <string>
#include <tuple>

#include <fmt/core.h>

#include "pipeline.h"

struct A {
  int divisor;

  A(int divisor) : divisor{divisor} {};

  std::tuple<int, int> run(double input, double to_add) const {
    return std::make_tuple(static_cast<int>(input) / divisor + to_add, divisor);
  }
};

struct do_not_copy {
  std::string str;

  do_not_copy(std::string str) : str{str} {};
  do_not_copy(do_not_copy &&moved) : str{moved.str} {};

  do_not_copy(do_not_copy const &) = delete;
  do_not_copy &operator=(do_not_copy const &) = delete;
  do_not_copy() = delete;
};

struct B {

  std::tuple<do_not_copy, int> run(int input, int divisor) const {
    return std::make_tuple(fmt::format("input // {} = {}", divisor, input),
                           4915);
  }
};

struct C {
  do_not_copy run(do_not_copy &&input, int) const { return std::move(input); }
};

struct D {
  std::string run(do_not_copy &&input) const { return input.str; }
};

int main() {
  baboon_tracking::pipeline pl{A{3}, B{}, C{}, D{}};

  fmt::print("result: {}\n", pl.process(10.3, 9));

  return EXIT_SUCCESS;
}
