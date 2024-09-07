# snakAI
Snake game for 'AI vs AI' or 'AI vs Human' combat

# Shortcomings
* Timing of snakes are handles with random ordering
* Snakes doesn't have ability to look further than their next move
* Escape mechanism is not fit for all cases
* Human input is taken by keyboard, which requires root permission for Ubuntu

# TO-DOs
* Snake timings can be done by assigning a thread to each snake. If race between processes are solved fastest snake wins fairly
* Another heuristic cost can be added to moves according to state after that move to help with move selection
* Different cases can be detected and path selection can be altered respect to them for different escape cases
* Another input format can be used for privacy and authorization concerns
