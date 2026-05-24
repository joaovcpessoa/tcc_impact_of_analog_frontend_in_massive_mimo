clear;clc;close all;

%% PATHS
% ####################################################################### %
current_dir = fileparts(mfilename('fullpath'));

env_file = fullfile(current_dir, '..', '.env');
env_vars = load_env(env_file);

simulation = env_vars.SIMULATION_SAVE_PATH;
output_dir = env_vars.PLOT_SAVE_PATH;
functions = env_vars.FUNCTIONS_PATH;

addpath(simulation);
addpath(functions);

load('amplitude_io_clip.mat');

savefig = 1;

%% PLOTTING PARAMETERS
% ####################################################################### %
graph_name = 'amplitude_io_clip.mat';

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

%% PLOT - IDEAL CLIPPING AMPLIFIER
% ####################################################################### %

figure;

for a0_idx = 1:N_A0  
    plot(amplitude_in, abs(squeeze(amplitude_out_clip(:, 1, a0_idx))), '-', 'LineWidth', linewidth);
    hold on;
end

xlabel('Amplitude de entrada', 'FontName', fontname, 'FontSize', fontsize);
ylabel('Amplitude de saída', 'FontName', fontname, 'FontSize', fontsize);

xlim([0 2.5]);
ylim([0 2.5]);

legend_text = {'$A_0 = 1$','$A_0 = 2$'};  
legend(legend_text, 'Location', 'southeast', 'FontSize', fontsize, 'FontName', fontname, 'Interpreter', 'latex');
legend box off;

set(gca, 'FontName', fontname, 'FontSize', fontsize);

if savefig == 1
    saveas(gcf,[output_dir graph_name],'png');
   % saveas(gcf,[output_dir graph_name],'fig');
   % saveas(gcf,[output_dir graph_name],'epsc2');
end

% %% PLOT - SSA AMPLIFIER
% % ####################################################################### %
% 
% figure;
% 
% for a0_idx = 1:N_A0
%     for p_idx = 1:length(p_values)        
%         plot(amplitude_in, squeeze(amplitude_out_ss(:, p_idx, a0_idx)), '-', 'LineWidth', linewidth);
%         hold on;
%     end
% end
% 
% xlabel('Amplitude de entrada', 'FontName', fontname, 'FontSize', fontsize);
% ylabel('Amplitude de saída', 'FontName', fontname, 'FontSize', fontsize);
% 
% legend_text = {'$p = 1, A_0 = 1$', '$p = 2, A_0 = 1$', '$p = 3, A_0 = 1$', ...
%                '$p = 1, A_0 = 2$', '$p = 2, A_0 = 2$', '$p = 3, A_0 = 2$'};
% xlim([0 5]);
% ylim([0 2]);
% 
% legend(legend_text, 'Location', 'southeast', 'FontSize', fontsize, 'FontName', fontname, 'Interpreter', 'latex', 'NumColumns', 2);
% legend box off;
% 
% set(gca, 'FontName', fontname, 'FontSize', fontsize);
% 
% %% PLOT - AMPLITUDE TWT AMPLIFIER
% % ####################################################################### %
% 
% figure;
% 
% for a0_idx = 1:N_A0
%     for param_idx = 1:N_params       
%         plot(amplitude_in, squeeze(amplitude_out_twt(:, param_idx, a0_idx)), '-', 'LineWidth', linewidth);
%         hold on;
%     end
% end
% 
% xlabel('Amplitude de entrada', 'FontName', fontname, 'FontSize', fontsize);
% ylabel('Amplitude de saída', 'FontName', fontname, 'FontSize', fontsize);
% 
% legend_text = {'$\mathcal{C}_1$', '$\mathcal{C}_2$', '$\mathcal{C}_3$'};  
% legend(legend_text, 'Location', 'northwest', 'FontSize', fontsize, 'FontName', fontname, 'Interpreter', 'latex');
% legend box off;
% grid off;
% 
% xlim([0 3.5]);
% ylim([0 3.5]);
% 
% set(gca, 'FontName', fontname, 'FontSize', fontsize);
% 
% %% PLOT - PHASE TWT AMPLIFIER
% % ####################################################################### %
% 
% figure;
% 
% for a0_idx = 1:N_A0
%     for param_idx = 1:N_params       
%         plot(amplitude_in, squeeze(phase_out_twt(:, param_idx, a0_idx)), '-', 'LineWidth', linewidth);
%         hold on;
%     end
% end
% 
% xlabel('Amplitude de entrada', 'FontName', fontname, 'FontSize', fontsize);
% ylabel('Fase de saída', 'FontName', fontname, 'FontSize', fontsize);
% 
% legend(legend_text, 'Location', 'northwest', 'FontSize', fontsize, 'FontName', fontname, 'Interpreter', 'latex');
% legend box off;
% grid off;
% 
% xlim([0 5]);
% 
% set(gca, 'FontName', fontname, 'FontSize', fontsize);