# Test all samples


#category = (ring :ambi, :bass, :bd, :drum, :elec, :guit, :loop, :misc, :perc, :sn, :tabla, :vinyl)
category = sample_groups.sort

# Load samples
puts "Caching samples .."
for idx in 0..category.size-1 do
    puts "  For Category #{category[idx]}"
    sample_names(category[idx]).each do |s|
      puts "    Load #{s} sample"
      load_samples s
    end
  end
  puts ""
  
  # Play samples
  puts "Play samples"
  for idx in 0..category.size-1 do
      with_sample_defaults amp: 4 do
        sample_names(category[idx]).sort.each do |s|
          puts "Play #{category[idx]}-#{s}"
          sample s
          sleep (sample_duration s) + 1
        end
      end
    end
