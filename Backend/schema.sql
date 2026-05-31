-- 1. Xóa các bảng cũ nếu tồn tại (cẩn thận khi chạy production)
DROP TABLE IF EXISTS "PROJECT" CASCADE;
DROP TABLE IF EXISTS "USER" CASCADE;
DROP TABLE IF EXISTS "STD_MOTOR" CASCADE;
DROP TABLE IF EXISTS "STD_CHAIN" CASCADE;
DROP TABLE IF EXISTS "STD_MATERIAL" CASCADE;
DROP TABLE IF EXISTS "STD_MODULE" CASCADE;
DROP TABLE IF EXISTS "STD_CENTER_DISTANCE" CASCADE;

-- 2. Tạo bảng USER
CREATE TABLE "USER" (
    "userID" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "userName" VARCHAR(255) NOT NULL,
    "joinedDate" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "password" VARCHAR(255) NOT NULL,
    "email" VARCHAR(255) UNIQUE NOT NULL
);

-- 3. Tạo bảng PROJECT
CREATE TABLE "PROJECT" (
    "projectID" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "projectName" VARCHAR(255) NOT NULL,
    "projectDescription" TEXT,
    "userID" UUID REFERENCES "USER"("userID") ON DELETE CASCADE,
    "createdDate" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Bảng tiêu chuẩn: STD_MOTOR
CREATE TABLE "STD_MOTOR" (
    "motorCode" VARCHAR(50) PRIMARY KEY,
    "P_dm" FLOAT NOT NULL,
    "n_dm" FLOAT NOT NULL,
    "torqueRatio" FLOAT NOT NULL
);

-- 5. Bảng tiêu chuẩn: STD_CHAIN
CREATE TABLE "STD_CHAIN" (
    "chainID" VARCHAR(50) PRIMARY KEY,
    "breakingLoad_Q" FLOAT NOT NULL,
    "massPerMeter_q" FLOAT NOT NULL,
    "pitch_p" FLOAT NOT NULL,
    "numStrands" INT NOT NULL DEFAULT 1
);

-- 6. Bảng tiêu chuẩn: STD_MATERIAL
CREATE TABLE "STD_MATERIAL" (
    "matID" VARCHAR(50) PRIMARY KEY,
    "matName" VARCHAR(255) NOT NULL,
    "sigmaHlim_base" FLOAT NOT NULL,
    "sigmaFlim_base" FLOAT NOT NULL,
    "sigma_ch" FLOAT NOT NULL,
    "sigma_b" FLOAT NOT NULL,
    "hardnessHB_max" FLOAT NOT NULL,
    "hardnessHB_min" FLOAT NOT NULL
);

-- 7. Bảng tiêu chuẩn: STD_MODULE
CREATE TABLE "STD_MODULE" (
    "modVal" FLOAT PRIMARY KEY,
    "prefSeries" INT NOT NULL DEFAULT 1
);

-- 8. Bảng tiêu chuẩn: STD_CENTER_DISTANCE
CREATE TABLE "STD_CENTER_DISTANCE" (
    "awValue" FLOAT PRIMARY KEY
);

-- =======================================================
-- BẬT ROW LEVEL SECURITY (RLS) - Bắt buộc trên Supabase
-- (Tạm thời cho phép Public đọc/ghi dễ dàng cho lúc dev)
-- =======================================================

ALTER TABLE "USER" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "PROJECT" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "STD_MOTOR" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "STD_CHAIN" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "STD_MATERIAL" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "STD_MODULE" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "STD_CENTER_DISTANCE" ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read-write for USER" ON "USER" FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public read-write for PROJECT" ON "PROJECT" FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public read-write for STD_MOTOR" ON "STD_MOTOR" FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public read-write for STD_CHAIN" ON "STD_CHAIN" FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public read-write for STD_MATERIAL" ON "STD_MATERIAL" FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public read-write for STD_MODULE" ON "STD_MODULE" FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public read-write for STD_CENTER_DISTANCE" ON "STD_CENTER_DISTANCE" FOR ALL USING (true) WITH CHECK (true);
