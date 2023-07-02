import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import time
import pandas as pd
import sys
import os
import uuid

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

        self.label_method = tk.Label(self, text="Which method do you want to run benchmarks for?")
        self.label_method.pack()
        self.selected_option = tk.StringVar()
        options = ["register users", "add admin relation", "delete users", "login users"]
        option_menu = ttk.OptionMenu(self, self.selected_option, options[0], *options)
        option_menu.pack()

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
        except ValueError as e:
            print(e)
            messagebox.showerror("Error", "Invalid input! Please enter numbers for iterations and users.")

    def register_users(self,db:BBDB,users_per_iteration:int,is_benchmark_test_method:bool=False) ->list:
        user_ids = []
        for i in range(users_per_iteration):
            username = f"username{uuid.uuid4()}"
            user_enc_res_id = f"user_enc_res_id{uuid.uuid4()}"
            user_id = db.register_user(username, user_enc_res_id)
            user_ids.append(user_id)
            if is_benchmark_test_method:
                self.progressbar["value"] += 1
                self.update_idletasks()

        return user_ids
    
    def delete_users(self,db:BBDB,user_ids:list,is_benchmark_test_method:bool=False):
        for user_id in user_ids:
            db.delUser(user_id)
            if is_benchmark_test_method:
                self.progressbar["value"] += 1
                self.update_idletasks()

    def add_admin_relation(self,db:BBDB,user_ids:list,is_benchmark_test_method:bool=False):
        for user_id in user_ids:
            db.addAdminRelation(user_id)
            if is_benchmark_test_method:
                self.progressbar["value"] += 1
                self.update_idletasks()

    def login_users(self,db:BBDB,user_ids:list,is_benchmark_test_method:bool=False):
        for user_id in user_ids:
            db.login_user(user_id)
            if is_benchmark_test_method:
                self.progressbar["value"] += 1
                self.update_idletasks()

    def run_iterations(self, iterations:int, users_per_iteration:int):
        total_execution_time = 0
        results = []
        self.progressbar["maximum"] = iterations * users_per_iteration
        self.progressbar["value"] = 0

        db = BBDB()  # Instantiate the BBDB class

        for i in range(iterations):

            # Run database operations here and measure the execution time
            if self.selected_option.get() == "register users":
                start_time = time.time()
                user_ids = self.register_users(db=db, users_per_iteration=users_per_iteration, is_benchmark_test_method=True)
                end_time = time.time()
                self.delete_users(db,user_ids)
            
            elif self.selected_option.get() == "delete users":
                user_ids = self.register_users(db=db, users_per_iteration=users_per_iteration)
                start_time = time.time()
                self.delete_users(db=db, user_ids=user_ids, is_benchmark_test_method=True)
                end_time = time.time()
            
            elif self.selected_option.get() == "add admin relation":
                user_ids = self.register_users(db=db, users_per_iteration=users_per_iteration)
                start_time = time.time()
                self.add_admin_relation(db=db,user_ids=user_ids, is_benchmark_test_method=True)
                end_time = time.time()
                self.delete_users(db=db, user_ids=user_ids)

            elif self.selected_option.get() == "login users":
                user_ids = self.register_users(db=db, users_per_iteration=users_per_iteration)
                start_time = time.time()
                self.login_users(db=db,user_ids=user_ids, is_benchmark_test_method=True)
                end_time = time.time()
                self.delete_users(db=db, user_ids=user_ids)

            iteration_execution_time = end_time - start_time
            total_execution_time += iteration_execution_time

            results.append((i + 1, iteration_execution_time))

            self.update_idletasks()
        
        # Add Average execution time to the results
        results.append(("Average", total_execution_time / iterations))

        # Add total execution time to the results
        results.append(("Total", total_execution_time))

        # Convert the results to a pandas DataFrame
        df = pd.DataFrame(results, columns=["Iteration", "Execution Time"])

        # Specify time unit (seconds)
        df["Execution Time"] = df["Execution Time"].apply(lambda x: f"{x:.6f} s")

        messagebox.showinfo("Benchmark Results", df.to_string(index=False))


if __name__ == "__main__":
    app = BenchmarkApp()
    app.mainloop()
