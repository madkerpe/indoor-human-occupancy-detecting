from localization.processing import ImageProcessor

proc = ImageProcessor()

print(sum(proc.weight_values))
print(proc.weight_step)
print(proc.weight_min)
print(proc.weight_values)