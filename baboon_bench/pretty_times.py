def print_region_start( name, level ):
    
    if level > 0:
        level = " " * level
    else:
        level = ""

    print( f"{level}{name}" )

def print_task_time_ms( name, start, end, level ):

    on = True
    if not on:
        return

    time = float( end - start ) / 1e6

    if level > 0:
        level = "|" + ("-" * level) + "> "
    else:
        level = ""
        
    adjust = " " * ( 40 - len(level + name) )

    if time < 100:
        print( f"{ level }{ name }:{adjust}{ round( time ) }ms")
    else:
        print( f"{ level }{ name }:{adjust}\033[91m{ round( time ) }ms\033[00m")
