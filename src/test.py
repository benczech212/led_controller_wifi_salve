test_data = ["#ffffff","#ff0000", "#00ff00","#0000ff","#000000"]



def hex_to_rgb(hex_val):
   colors = []
   hex_val = hex_val[1:]
   for i in range(0,6,2):
      val = hex_val[i:i+2]
      val = int(val,16)
      colors.append(val)
   return colors

for i in test_data:
   print(hex_to_rgb(i))