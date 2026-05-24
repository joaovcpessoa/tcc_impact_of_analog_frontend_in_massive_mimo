function x_normalized = normalize_decoded_signal(decoder, decoder_type, M, s, N_SNR)

    disp("Size of decoder: ");
    disp(size(decoder));
    disp("Size of s: ");
    disp(size(s));
    disp("Size of s.': ");
    disp(size(s.'));
    
    switch upper(decoder_type)
        case {'ZF', 'MF'}
            x = decoder * s.';
            x_normalized = zeros(size(x));            
            for m = 1:M
                Px = norm(x(m, :))^2 / length(x(:, m));
                x_normalized(m, :) = x(m, :) / sqrt(Px);
            end
        case 'MMSE'
            x = zeros(K, N_BLK, N_SNR);
            x_normalized = zeros(K, N_BLK, N_SNR);
            for snr_idx = 1:N_SNR
                x(:, :, snr_idx) = decoder(:, :, snr_idx) * s.';
                for m = 1:M
                    Px = norm(x(m, :, snr_idx))^2 / length(x(:, m, snr_idx));
                    x_normalized(m, :, snr_idx) = x(m, :, snr_idx) / sqrt(Px);
                end
            end
        otherwise
            error('Invalid decoder type. Choose "ZF", "MF", or "MMSE".');
    end
end