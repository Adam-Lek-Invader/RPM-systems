import csv, os, json
import numpy as np

DEFAULT_CONFIG = {
    "paths": ["~","~","~","~"],
    "paths_names": ["Path1","Path2","Path3","Path4"],
    "trajectory_mark_type": "PosTraj",
    "SphereType": "Icosphere",
    "n": 3,
    "nei_cnt": 6
}

def load_json_config(file_name:str)->dict:
    if os.path.exists(file_name) == False:
        return DEFAULT_CONFIG
    with open(file_name, 'r') as f:
        return json.load(f)

def save_json_config(file_name:str, config_dict:dict):
    with open(file_name, 'w') as f:
        json.dump(config_dict, f, indent=4)

class Vector3:
    def __init__(self):
        pass

class CSV_DataParser:
    
    def __init__(self, FileDir, maxBuffCnt=50):
        if os.path.exists(FileDir) == False:
            raise ValueError("file does not exists")
        self.FILE_Dir = FileDir
        self.MAX_BUFF_CNT = maxBuffCnt
        self.csv_names = []
        self.csv_buffers = []
        self.csv_buff_cnt = 0
        
    def __parse_Vector3(self, str_vec3:str)->np.ndarray:
         vec3 = np.fromstring(str_vec3, dtype=np.float32, sep="|")
         return vec3
         

    def gen_get_data(self):
        '''
        generator function to be used inside for each - "for (col names, buffers, buff row count) in gen_get_data()"
        '''
        with open(self.FILE_Dir, newline='\n') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            # parse header row
            row = csv_reader.__next__()
            for name in row:
                self.csv_names.append(name)
            # parse first row with data to check types
            row = csv_reader.__next__()
            for num in row:
                if '.' in num:
                    if '|' in num:
                        parsed_type = Vector3
                        parsed_num = self.__parse_Vector3(num)
                    else:
                        parsed_type = np.float32
                        parsed_num = parsed_type(num)
                else:
                    parsed_type = np.int32
                    parsed_num = int(num)
                    # @@@ add validation for cutoff errpr
                if parsed_type == Vector3:
                    buffer = np.zeros(shape=(self.MAX_BUFF_CNT,3), dtype=np.float32)
                    buffer[0,:] = parsed_num
                else:
                    buffer = np.zeros(shape=(self.MAX_BUFF_CNT), dtype=parsed_type)
                    buffer[0] = parsed_num
                self.csv_buffers.append( buffer )
            self.csv_buff_cnt = 1
            # parse rest of the file
            for row in csv_reader:
                # @@@ blank lines parse
                for i,num in enumerate(row):
                    cur_buff = self.csv_buffers[i]
                    cur_buff[self.csv_buff_cnt] = np.fromstring(num, sep="|", dtype=cur_buff.dtype)
                self.csv_buff_cnt += 1
                
                # yield logic
                if self.csv_buff_cnt == self.MAX_BUFF_CNT:
                    ref_buff = (self.csv_names, self.csv_buffers, self.csv_buff_cnt)
                    yield ref_buff
                    self.csv_buff_cnt = 0
                    # for safety zeroing all buffers
                    for cur_buff in self.csv_buffers:
                        cur_buff = np.zeros(shape=cur_buff.shape, dtype=cur_buff.dtype)

            # end of file logic
            # reshaping buffers to current real sizes
            for i,cur_buff in enumerate(self.csv_buffers):
                if len(cur_buff.shape) == 1:
                    temp_buff = cur_buff[0:self.csv_buff_cnt]
                elif len(cur_buff.shape) == 2:
                    temp_buff = cur_buff[0:self.csv_buff_cnt,:]
                else:
                    raise TypeError("Unrecognised Shape/DataType")
                  
                self.csv_buffers[i] = temp_buff
            ref_buff = (self.csv_names, self.csv_buffers, self.csv_buff_cnt)
            yield ref_buff
