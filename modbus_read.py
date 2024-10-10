import serial.tools.list_ports
from pymodbus.client import ModbusSerialClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
import serial

# 列出所有可用的串口
ports = list(serial.tools.list_ports.comports())
print("可用的串口:")
for i, port in enumerate(ports):
    print(f"{i}: {port.device}")

# 选择一个串口
port_index = int(input("请输入串口编号: "))
port = ports[port_index].device

# 输入从站 ID
slave_id = int(input("请输入从站 ID (十进制): "))

# 配置串口参数
baudrate = 9600
stopbits = serial.STOPBITS_ONE
bytesize = serial.EIGHTBITS
parity = serial.PARITY_NONE

# 创建 Modbus 客户端
client = ModbusSerialClient(
    port=port,
    baudrate=baudrate,
    stopbits=stopbits,
    bytesize=bytesize,
    parity=parity,
    timeout=1
)

# 连接到 Modbus 设备
if not client.connect():
    print("无法连接到 Modbus 设备")
    exit()

try:
    # 读取寄存器
    def read_float_register(address):
        count = 2  # 浮点数需要2个寄存器
        result = client.read_holding_registers(address, count, slave=slave_id)
        if not result.isError():
            decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.BIG, wordorder=Endian.BIG)
            return decoder.decode_32bit_float()
        else:
            print(f"读取错误: {result}")
            return None

    # 读取多个寄存器数据
    data_points = {
        "Frequency": 1052,
        "Voltage A": 1000,
        "Voltage B": 1002,
        "Voltage C": 1004,
        "Current A": 1006,
        "Current B": 1008,
        "Current C": 1010,
        "Active Power A": 1012,
        "Active Power B": 1014,
        "Active Power C": 1016,
        "Reactive Power A": 1018,
        "Reactive Power B": 1020,
        "Reactive Power C": 1022,
        "Apparent Power A": 1024,
        "Apparent Power B": 1026,
        "Apparent Power C": 1028,
        "Power Factor A": 1030,
        "Power Factor B": 1032,
        "Power Factor C": 1034,
        "Total Active Power": 1044,
        "Total Reactive Power": 1046,
        "Total Apparent Power": 1048,
        "Total Power Factor": 1050,
        "Total Import Active Energy": 1054,
        "Total Import Export Energy": 1056,
        "Total Import and Expor active energy": 1058,
        "Phase A Import active energy": 1060,
        "Phase A Export active energy": 1062,
        "Phase A Import and Export active energy": 1064,
        "Phase B Import active energy": 1066,
        "Phase B Export active energy": 1068,
        "Phase B Import and Export active energy": 1070,
        "Phase C Import active energy": 1072,
        "Phase C Export active energy": 1074,
        "Phase C Import and Export active energy": 1076
    }

    for name, address in data_points.items():
        value = read_float_register(address)
        print(f"{name}: {value}")

finally:
    # 断开连接
    client.close()
