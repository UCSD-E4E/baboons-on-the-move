#pragma once

#include <condition_variable>
#include <cstdint>
#include <functional> //bind
#include <future>     //packaged_task
#include <mutex>
#include <queue>
#include <thread>
#include <type_traits> //invoke_result
#include <vector>

namespace baboon_tracking {
class thread_pool {
public:
  thread_pool(std::size_t thread_count = std::thread::hardware_concurrency());
  ~thread_pool();

  // F is Callable, and invoking F with ...Args should be well-formed
  template <typename F, typename... Args>
  auto execute(F function, Args &&...args) {
    // std::unique_lock<std::mutex> queue_lock(task_mutex, std::defer_lock);
    std::packaged_task<std::invoke_result_t<F, Args...>()> task_pkg(
        [f = std::move(function),
         fargs = std::make_tuple(std::forward<Args>(args)...)]() mutable {
          return std::apply(std::move(f), std::move(fargs));
        });
    std::future<std::invoke_result_t<F, Args...>> future =
        task_pkg.get_future();

    {
      std::unique_lock lk{task_mutex};
      // This lambda move-captures the packaged_task declared above. Since the
      // packaged_task type is not CopyConstructible, the function is not
      // CopyConstructible either)— hence the need for a task_container to wrap
      // around it.
      tasks.emplace(std::unique_ptr<task_container_base>(new task_container(
          [task = std::move(task_pkg)]() mutable { task(); })));
    }

    task_cv.notify_one();

    return std::move(future);
  }

private:
  //  task_container_base and task_container exist simply as a wrapper around a
  //  MoveConstructible—but not CopyConstructible—Callable object. Since an
  //  std::function requires a given Callable to be CopyConstructible, we cannot
  //  construct one from a lambda function that captures a non-CopyConstructible
  //  object (such as the packaged_task declared in execute)—because a lambda
  //  capturing a non-CopyConstructible object is not CopyConstructible.

  //  task_container_base exists only to serve as an abstract base for
  //  task_container. The dynamic dispatch is required to erase the type of the
  //  callable.
  class task_container_base {
  public:
    virtual ~task_container_base(){};

    virtual void operator()() = 0;
  };

  //  task_container takes a typename F, which must be Callable and
  //  MoveConstructible. Furthermore, F must be callable with no arguments; it
  //  can, for example, be a bind object with no placeholders. F may or may not
  //  be CopyConstructible.
  template <typename F> class task_container : public task_container_base {
  public:
    //  Here, std::forward is needed because we need the construction of f *not*
    //  to bind an lvalue reference—it is not a guarantee that an object of type
    //  F is CopyConstructible, only that it is MoveConstructible.
    task_container(F &&func) : f{std::forward<F>(func)} {}

    void operator()() override { f(); }

  private:
    F f;
  };

  // This is a hack... GCC <= 11 erroneously doesn't support deduction guides in
  // classes. Will fail to compile without the deduction guide if you use this
  // class.
#if __GNUC__ > 11
  // Deduction guide so that we can infer task_container from some callable F
  template <typename F> task_container(F) -> task_container<std::decay_t<F>>;
#endif

  std::vector<std::thread> threads;
  std::queue<std::unique_ptr<task_container_base>> tasks;
  std::mutex task_mutex;
  std::condition_variable task_cv;
  bool stop_threads = false;

  std::condition_variable max_tasks_cv;
};
} // namespace baboon_tracking
