Design and test a prompt that classifies cargo items as DNG (dangerous) or NEU (neutral).

Requirements:
1. fetch_items first to see what you're working with
2. reset_budget before each test run
3. Prompt template must be ≤100 tokens when filled in (check the longest description)
4. Reactor/nuclear/fuel cassette parts MUST always output NEU (even if dangerous)
5. Static instructions first for cache efficiency, {id} and {description} at the end
6. Iterate until hub returns {FLG:...}
