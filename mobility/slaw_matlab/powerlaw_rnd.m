function x = powerlaw_rnd(alpha, min_size, max_size, num_step, sc_pause, ...
    p_mode)
% generate random values from power-law distribution
% 0 < alpha <= 2
% p_mode
%   1: stabrnd
%   2: reverse computation

x = [];
if p_mode == 1
    %display(p_mode);
    %display(sc_pause);
    while length(x) < num_step
        temp_x = stabrnd(alpha,0,sc_pause,0,1,num_step);
        temp_x = temp_x(find(temp_x > min_size));
        temp_x = temp_x(find(temp_x < max_size));
        x = [x temp_x];
    end
elseif p_mode == 2
    alpha = alpha + 1;
    while length(x) < num_step
        temp_x = rand(num_step,1);
        l = power(temp_x,1/(1-alpha));
        l = l * min_size;
        l = l(find(l < max_size));
        x = [x; l];
    end
end
x = x(1:num_step);
