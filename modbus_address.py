import serial.tools.list_ports
from pymodbus.client import ModbusSerialClient
import serial

# 列出所有可用的串口
ports = list(serial.tools.list_ports.comports())
print("可用的串口:")
for i, port in enumerate(ports):
    print(f"{i}: {port.device}")

# 选择一个串口
port_index = int(input("请输入串口编号: "))
port = ports[port_index].device

# 输入当前从站 ID
current_slave_id = int(input("请输入当前从站 ID (十进制): "))

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
    # 发送命令
    def send_command(address, value, slave_id):
        result = client.write_register(address, value, slave=slave_id)
        if not result.isError():
            print(f"命令发送成功: 地址 {address}, 值 {value}")
        else:
            print(f"命令发送失败: {result}")

    # 更改 Modbus 地址
    new_address = int(input("请输入新的 Modbus 地址 (1-247): "))
    if 1 <= new_address <= 247:
        modbus_address_register = 6000  # 寄存器地址
        send_command(modbus_address_register, new_address, current_slave_id)
    else:
        print("无效的 Modbus 地址")

finally:
    # 断开连接
    client.close()
