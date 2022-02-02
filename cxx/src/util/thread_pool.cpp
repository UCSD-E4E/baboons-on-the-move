#include "thread_pool.h"

namespace baboon_tracking {
thread_pool::thread_pool(std::size_t thread_count) {
  for (size_t i = 0; i < thread_count; ++i) {
    // start waiting threads. Workers listen for changes through
    //  the thread_pool member condition_variable
    threads.emplace_back(std::thread([&]() {
      std::unique_lock queue_lock(task_mutex, std::defer_lock);

      while (true) {
        queue_lock.lock();
        task_cv.wait(queue_lock,
                     [&]() { return !tasks.empty() || stop_threads; });

        // Used by dtor to stop all threads without having to
        // unceremoniously stop tasks. The tasks must all be
        // finished, lest we break a promise and risk a `future`
        // object throwing an exception.
        if (stop_threads && tasks.empty())
          return;

        // To initialize temp_task, we must move the unique_ptr
        // from the queue to the local stack. Since a unique_ptr
        // cannot be copied (obviously), it must be explicitly
        // moved. This transfers ownership of the pointed-to
        // object to *this, as specified in 20.11.1.2.1
        // [unique.ptr.single.ctor].
        auto temp_task = std::move(tasks.front());

        tasks.pop();
        queue_lock.unlock();

        // max_tasks_cv.notify_all();

        (*temp_task)();
      }
    }));
  }
}

thread_pool::~thread_pool() {
  stop_threads = true;
  task_cv.notify_all();

  for (std::thread &thread : threads) {
    thread.join();
  }
}
} // namespace baboon_tracking
