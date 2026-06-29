insert into public.app_users (id,username,password_hash,nama,role,guru_id,is_active) values
('USER-ADMIN','admin','8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92','Admin SIPINTAR-MI','admin','G-ADMIN',true),
('USER-HENI','heni','8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92','Heni Windawati','guru','G-HENI',true),
('USER-AHMAD','ahmad','8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92','Ahmad Zaenal Arifin','guru','G-AHMAD',true)
on conflict (username) do update set password_hash=excluded.password_hash,nama=excluded.nama,role=excluded.role,guru_id=excluded.guru_id,is_active=true;
