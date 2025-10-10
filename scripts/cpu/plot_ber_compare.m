%% CLEAR
% ####################################################################### %

clear;
close all;
clc;

%% PATHS
% ####################################################################### %

current_dir = fileparts(mfilename('fullpath'));

env_file = fullfile(current_dir, '..', '..', '.env');
env_vars = load_env(env_file);

% simulation_dir = env_vars.GPU_SIMULATION_SAVE_PATH;
simulation_dir = env_vars.SIMULATION_PATH_64QAM;
plot_dir = env_vars.GPU_PLOT_BER_PATH;
functions_dir = env_vars.CPU_FUNCTIONS_PATH;

addpath(simulation_dir);
addpath(functions_dir);
addpath(plot_dir);

savefig = 1;

%% PLOTTING PARAMETERS
% ####################################################################### %

linewidth  = 2;
fontname   = 'Times New Roman';
fontsize   = 20;
markersize = 10;

colors = [0.0000 0.0000 0.0000;
          0.0000 0.4470 0.7410;
          0.8500 0.3250 0.0980;
          0.9290 0.6940 0.1250;
          0.4940 0.1840 0.5560;
          0.4660 0.6740 0.1880;
          0.6350 0.0780 0.1840;
          0.3010 0.7450 0.9330];

%% PLOT COMPARATIVO
% ####################################################################### %

x = 'dl';
y = 'mmse';
z = '64qam';

filename = sprintf('%s_ber_%s_ss_256_64.mat', x, y);
load(filename);

BER_per_user_64     = mean(BER, 1);
avg_H_BER_64        = mean(BER_per_user_64, 5);
avg_BER_per_user_64 = mean(avg_H_BER_64, 6);

filename = sprintf('%s_ber_%s_ss_256_128.mat', x, y);
load(filename);

BER_per_user_128     = mean(BER, 1);
avg_H_BER_128        = mean(BER_per_user_128, 5);
avg_BER_per_user_128 = mean(avg_H_BER_128, 6);

filename = sprintf('%s_ber_%s_ss_256_256.mat', x, y);
load(filename);

BER_per_user_256     = mean(BER, 1);
avg_H_BER_256        = mean(BER_per_user_256, 5);
avg_BER_per_user_256 = mean(avg_H_BER_256, 6);

disp(size(avg_BER_per_user_256));

figure;
set (gcf, "Position", [0, 0, 800, 600]);

semilogy(SNR, avg_BER_per_user_64(:, :, 1, 1) ,'-' , 'LineWidth', linewidth, 'MarkerSize', markersize, 'Color', colors(1,:));
hold on;
semilogy(SNR, avg_BER_per_user_128(:, :, 1, 1),'--', 'LineWidth', linewidth, 'MarkerSize', markersize, 'Color', colors(1,:));
semilogy(SNR, avg_BER_per_user_256(:, :, 1, 1),':' , 'LineWidth', linewidth, 'MarkerSize', markersize, 'Color', colors(1,:));

semilogy(SNR, avg_BER_per_user_64(:, :, 1, 1) ,'-' , 'LineWidth', linewidth, 'MarkerSize', markersize, 'Color', colors(2,:));
semilogy(SNR, avg_BER_per_user_64(:, :, 2, 1) ,'-' , 'LineWidth', linewidth, 'MarkerSize', markersize, 'Color', colors(3,:));
semilogy(SNR, avg_BER_per_user_64(:, :, 2, 2) ,'-' , 'LineWidth', linewidth, 'MarkerSize', markersize, 'Color', colors(4,:));
% semilogy(SNR, avg_BER_per_user_64(:, :, 2, 3) ,'-' , 'LineWidth', linewidth, 'MarkerSize', markersize, 'Color', colors(5,:));

semilogy(SNR, avg_BER_per_user_128(:, :, 1, 1),'--', 'LineWidth', linewidth, 'MarkerSize', markersize, 'Color', colors(2,:));
semilogy(SNR, avg_BER_per_user_128(:, :, 2, 1),'--', 'LineWidth', linewidth, 'MarkerSize', markersize, 'Color', colors(3,:));
semilogy(SNR, avg_BER_per_user_128(:, :, 2, 2),'--', 'LineWidth', linewidth, 'MarkerSize', markersize, 'Color', colors(4,:));
% semilogy(SNR, avg_BER_per_user_128(:, :, 2, 3),'--', 'LineWidth', linewidth, 'MarkerSize', markersize, 'Color', colors(5,:));

semilogy(SNR, avg_BER_per_user_256(:, :, 1, 1),':' , 'LineWidth', linewidth, 'MarkerSize', markersize, 'Color', colors(2,:));
semilogy(SNR, avg_BER_per_user_256(:, :, 2, 1),':' , 'LineWidth', linewidth, 'MarkerSize', markersize, 'Color', colors(3,:));
semilogy(SNR, avg_BER_per_user_256(:, :, 2, 2),':' , 'LineWidth', linewidth, 'MarkerSize', markersize, 'Color', colors(4,:));
% semilogy(SNR, avg_BER_per_user_256(:, :, 2, 3),':' , 'LineWidth', linewidth, 'MarkerSize', markersize, 'Color', colors(5,:));


xlabel('SNR (dB)', 'FontName', fontname, 'FontSize', fontsize);
ylabel('BER', 'FontName', fontname, 'FontSize', fontsize);
    
legend_text = {'$K = 64$','$K = 128$','$K = 256$', 'Ideal', '$A = 0.5$', '$A = 1.0$'};
legend(legend_text, 'Location', 'southwest', ...
    'NumColumns', 2, 'FontSize', fontsize, 'FontName', fontname, 'Interpreter', 'latex');
legend box off;

set(gca, 'FontName', fontname, 'FontSize', fontsize);
ylim([1e-3 1])

graph_name = sprintf('%s_ber_compare_%s_%s', x, y, z);


if savefig == 1
    saveas(gcf, fullfile(plot_dir, [graph_name '.eps']), 'epsc2');
    saveas(gcf, fullfile(plot_dir, [graph_name '.png']), 'png');
end


