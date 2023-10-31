# @Author: Anna Prado
# @Date: 2020-11-15
# @Email: anna.prado@tum.de
# @Last modified by: Alba Jano

import matlab.engine  # requires Python 3.7 (not 3.8)


class GenerateMobility:
    def __init__(self, num_users, x_max, y_max, thours):
        self.num_users: float = num_users
        # self.size_max: float = size_max  # all vars have to be float
        self.x_max: float = x_max
        self.y_max: float = y_max
        self.Thours: float = thours
        self.MIN_PAUSE: float = 30  # sec
        self.MAX_PAUSE: float = 60 * 60
        self.beta: float = 1
        self.n_wp: float = 75
        self.B_range: float = min(self.x_max, self.y_max)/10  # 60  # todo: set a reasonable value
        self.dist_alpha: float = 3
        self.v_Hurst: float = 0.95
        self.folder_name = "mobility_traces"

        self.filename: str = ""
        self.engine = None

    def _convert_vars_to_float(self):
        # Convert variables to float because Python float is double in matlab,
        # otherwise there are errors in the Matlab code
        self.num_users = float(self.num_users)
        self.x_max = float(self.x_max)
        self.y_max = float(self.y_max)
        self.Thours = float(self.Thours)
        self.MIN_PAUSE = float(self.MIN_PAUSE)
        self.MAX_PAUSE = float(self.MAX_PAUSE)
        self.beta = float(self.beta)
        self.n_wp = float(self.n_wp)
        self.B_range = float(self.B_range)
        self.dist_alpha = float(self.dist_alpha)
        self.v_Hurst = float(self.v_Hurst)
        # self._log("Converted int varibles to float")

    def _create_filename(self):
        self.filename += self.folder_name
        self.filename += "/traces_"
        self.filename += f"{self.num_users}users"
        self.filename += f"_{self.x_max}x{self.y_max}size"
        self.filename += f"_{self.v_Hurst}hurst"
        self.filename += f"_{self.Thours}hours"
        self.filename += ".mat"
        # self._log(f"Mobility traces will be saved to {self.filename}")

    def genetate_mobility_traces(self):
        self._start_matlab_engine()
        self._create_filename()
        self._convert_vars_to_float()
        # self._log(f"Going to generate traces for {self.num_users} users, {self.x_max}x{self.y_max} size and {self.Thours} hours")
        # todo: it only works when files from mobility file are in the main folder.
        status = self.engine.run_SLAW_model(self.num_users, self.x_max, self.y_max, self.Thours,
                                            self.MIN_PAUSE, self.MAX_PAUSE, self.beta, self.n_wp,
                                            self.B_range, self.dist_alpha, self.v_Hurst,
                                            self.filename)
        if status:
            print("Generate mobility traces")
        else:
            raise ValueError("Matlab could not generate SLAW mobility traces")
        self._stop_matlab_engine()
        return self.filename

    def _start_matlab_engine(self):
        self.engine = matlab.engine.start_matlab()
        # self._log("Started matlab engine")
        self.engine.addpath('~/5g-and-beyond-simulator-2020/slaw_matlab')

    def _stop_matlab_engine(self):
        self.engine.quit()
        # self._log("Done. Stopped matlab engine")


