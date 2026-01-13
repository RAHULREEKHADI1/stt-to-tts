import React, { useEffect, useState } from "react";
import API from "../api/api";
import { CheckCircle2, Circle, Loader2, ListTodo, ClipboardCheck } from "lucide-react";

interface Task {
  _id: string;
  title: string;
  completed: boolean;
}

const TaskList: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState<string | null>(null);

  const fetchTasks = async () => {
    try {
      const res = await API.get<Task[]>("/tasks");
      setTasks(Array.isArray(res.data) ? res.data : []);
    } catch {
      setTasks([]);
    } finally {
      setLoading(false);
    }
  };

  const markComplete = async (taskId: string) => {
    setProcessingId(taskId);
    try {
      console.log(taskId,"taskId");
      
      const res = await API.patch<Task>(`/tasks/${taskId}/update`,{completed:true});
      setTasks(prev =>
        prev.map(task => (task._id === taskId ? res.data : task))
      );
    } catch (err) {
      console.error("Failed to complete task", err);
    } finally {
      setProcessingId(null);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-12 space-y-4">
        <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
        <p className="text-gray-500 animate-pulse">Loading your agenda...</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6 p-2">
      <div className="flex items-center justify-between border-b border-gray-100 pb-4">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-indigo-100 rounded-lg">
            <ListTodo className="w-5 h-5 text-indigo-600" />
          </div>
          <h3 className="text-xl font-bold text-gray-800">Your Tasks</h3>
        </div>
        <span className="bg-indigo-50 text-indigo-700 text-xs font-bold px-2.5 py-1 rounded-full uppercase tracking-wider">
          {tasks.filter(t => !t.completed).length} Pending
        </span>
      </div>

      {tasks.length === 0 && (
        <div className="text-center py-16 bg-gray-50 rounded-2xl border-2 border-dashed border-gray-200">
          <ClipboardCheck className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 font-medium">No tasks found. Relax!</p>
        </div>
      )}

      <ul className="grid gap-3">
        {tasks.map((task, index) => (
          <li
            key={task._id || index}
            className={`group relative flex items-center justify-between p-4 rounded-2xl transition-all duration-300 border ${
              task.completed
                ? "bg-gray-50/50 border-gray-100 opacity-75"
                : "bg-white border-gray-200 shadow-sm hover:shadow-md hover:border-indigo-200"
            }`}
          >
            <div className="flex items-center gap-4">
              <span className="shrink-0 w-8 h-8 flex items-center justify-center rounded-full bg-gray-100 text-gray-500 text-sm font-bold group-hover:bg-indigo-100 group-hover:text-indigo-600 transition-colors">
                {index + 1}
              </span>
              <span
                className={`text-base font-medium transition-all ${
                  task.completed ? "text-gray-400 line-through" : "text-gray-700"
                }`}
              >
                {task.title}
              </span>
            </div>

            <div className="flex items-center gap-3">
              {task.completed ? (
                <div className="flex items-center gap-1.5 text-green-600 bg-green-50 px-3 py-1 rounded-full text-xs font-bold uppercase">
                  <CheckCircle2 className="w-4 h-4" />
                  Done
                </div>
              ) : (
                <button
                  disabled={processingId === task._id}
                  onClick={() => markComplete(task._id)}
                  className="flex items-center gap-2 px-4 py-2 bg-white hover:bg-indigo-600 text-indigo-600 hover:text-white border border-indigo-200 hover:border-indigo-600 rounded-xl text-sm font-bold transition-all disabled:opacity-50"
                >
                  {processingId === task._id ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Circle className="w-4 h-4" />
                  )}
                  Mark Done
                </button>
              )}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default TaskList;