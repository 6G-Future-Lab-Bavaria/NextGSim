function status = run_SLAW_model(num_user, x_max, y_max, Thours, MIN_PAUSE, MAX_PAUSE, beta, n_wp, B_range, dist_alpha, v_Hurst, filename)
% Just copied this code from generate_slaw.m script to create a function
% that can be run from Python
%% Fixed
% num_user=20;
% size_max=500;
% Thours= 100; % check
% MIN_PAUSE=30;  % seconds 
% MAX_PAUSE=700*60;
% beta=1;
for seed=1%8:10
    counter=0;
    for i=1%0.1:0.1:0.7
        counter=counter+1;
        %% i dependent
        % n_wp=75 %50+450*i;
        % B_range=60 %25+250*i;
        % dist_alpha=3.5 %1.5+4.5*i;
        % v_Hurst=0.95 %0.55+0.4*i;
        %subplot(3,3,counter)
        try
        %% Generate user movements
        trace=SLAW_MATLAB(dist_alpha, num_user, x_max, y_max, n_wp, v_Hurst,...
            Thours, B_range, beta, MIN_PAUSE, MAX_PAUSE);
        % filename = strcat('mobility_traces/traces_',num2str(1))%,'seed',num2str(seed))
        %hold on
        %plot(trace(:,300,1),trace(:,300,2),'r*')
        save(filename)
        status = 1;
        catch
           disp('bad') 
           status = 0;
        end
    end
end


end 