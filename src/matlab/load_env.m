function env_vars = load_env(env_file)
    env_vars = struct();
    
    if exist(env_file, 'file') == 2
        fid = fopen(env_file, 'r');
        while ~feof(fid)
            line = strtrim(fgetl(fid));
            if isempty(line) || startsWith(line, '#')
                continue;
            end
            tokens = regexp(line, '^(.*?)=(.*)$', 'tokens');
            if ~isempty(tokens)
                key = strtrim(tokens{1}{1});
                value = strtrim(tokens{1}{2});
                env_vars.(key) = value;
            end
        end
        fclose(fid);
    else
        error('Arquivo .env não encontrado.');
    end
end
