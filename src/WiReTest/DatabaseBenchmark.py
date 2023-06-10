import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import time
import pandas as pd
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'DBM'))
from DatabaseManagement import BBDB


class BenchmarkApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Database Benchmark Program")
        self.geometry("500x350")

        self.label_iterations = tk.Label(self, text="Enter the number of iterations:")
        self.label_iterations.pack()

        self.entry_iterations = tk.Entry(self)
        self.entry_iterations.pack()

        self.label_users = tk.Label(self, text="Enter the number of users to register in each iteration:")
        self.label_users.pack()

        self.entry_users = tk.Entry(self)
        self.entry_users.pack()

        self.button = tk.Button(self, text="Run Benchmark", command=self.run_benchmark)
        self.button.pack()

        self.progressbar = ttk.Progressbar(self, mode="determinate", length=200)
        self.progressbar.pack()

    def run_benchmark(self):
        try:
            iterations = int(self.entry_iterations.get())
            users_per_iteration = int(self.entry_users.get())
            self.button.configure(state=tk.DISABLED)
            self.label_wait = tk.Label(self, text="Please wait...")
            self.label_wait.pack()
            self.run_iterations(iterations, users_per_iteration)
            self.button.configure(state=tk.NORMAL)
            self.label_wait.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid input! Please enter numbers for iterations and users.")

    def run_iterations(self, iterations, users_per_iteration):
        total_execution_time = 0
        results = []
        self.progressbar["maximum"] = iterations * users_per_iteration
        self.progressbar["value"] = 0

        db = BBDB()  # Instantiate the BBDB class

        for i in range(iterations):
            start_time = time.time()

            # Run database operations here and measure the execution time
            execution_time = self.run_database_operations(db, users_per_iteration)

            end_time = time.time()
            iteration_execution_time = end_time - start_time
            total_execution_time += iteration_execution_time

            results.append((i + 1, iteration_execution_time))

            self.update_idletasks()

        # Add total execution time to the results
        results.append(("Total", total_execution_time))

        # Convert the results to a pandas DataFrame
        df = pd.DataFrame(results, columns=["Iteration", "Execution Time"])

        # Specify time unit (seconds)
        df["Execution Time"] = df["Execution Time"].apply(lambda x: f"{x:.6f} s")

        messagebox.showinfo("Benchmark Results", df.to_string(index=False))

    def run_database_operations(self, db, users_per_iteration):
        start_time = time.time()

        # Delete existing users (uncomment if necessary)
        """
        existing_users = db.getUsers()
        for user_id in existing_users:
            db.delUser(user_id)
        """

        # Register multiple users
        user_ids = []
        for i in range(users_per_iteration):
            username = f"username{i + 1}"
            user_enc_res_id = f"user_enc_res_id{i + 1}"
            user_id = db.register_user(username, user_enc_res_id)
            user_ids.append(user_id)
            self.progressbar["value"] += 1
            self.update_idletasks()

        # Add admin relation for each user
        for user_id in user_ids:
            db.addAdminRelation(user_id)

        # Delete all users
        for user_id in user_ids:
            db.delUser(user_id)

        end_time = time.time()
        execution_time = end_time - start_time

        return execution_time


if __name__ == "__main__":
    app = BenchmarkApp()
    app.mainloop()
