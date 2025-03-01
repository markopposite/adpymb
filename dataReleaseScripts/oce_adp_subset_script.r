########################################################################################
#### Info: takes in raw adcp *r.000 file and outputs csv tables for each beam and avg
########################################################################################
#### Imports 
########################################################################################
library(dplyr)
library(lubridate)
library(oce)

# ---- 
########################################################################################
# Must manually define data ID and push/pull directories before running
########################################################################################

# Identifier unique to the files used for each lake and each year
adp_id_pre <- 'SEN19'
# # for use with directory and file naming conventions
adp_id <- 'SEN19280'

# define the adcp data file id and directory subfolder to store the csv table files
csv_dir <- "/home/mpoe/adcp_habs/data/adcp_data_tables/"
temp_dir <- paste(csv_dir, '/', adp_id, '/', sep='')

# create the directory using the id
dir.create(temp_dir)
csv_data <- temp_dir

# ---- 
########################################################################################
#### Dataframe and variable definitions
########################################################################################

# # read adcp data into oce package
adcp <- read.oce(df_adcp)
cc <- adcp
# # for coordinate transformation, necessary for specific lake-years, not all
# cc <- xyzToEnu(adcp, 12) # coord transformation to enu; 12 is the dec. from true north

a <- cc[['a','numeric']]
v <- cc[['v']] 
q <- cc[['q', 'numeric']]
g <- cc[['g', 'numeric']]

depth <- cc[['distance']]
time <- cc[["time"]]
x_i <- cc[['xmitCurrent']]
x_v <- cc[['xmitVoltage']]
roll <- cc[['roll']]
pitch <- cc[['pitch']]
head <- cc[['heading']]
amb_temp <- cc[['ambientTemp']]
att_temp <- cc[['attitudeTemp']]
temp <- cc[['temperature']]

ln <- length(cc[['distance']])
ln_prof <- length(cc[['time']])

# create a list of depths for beam array column names
names <- NULL
for (i in depth){
    names <- append(names, i) 
}

# ---- 
########################################################################################
#### Build and write the time series and bin tables to disk ----
########################################################################################

ts_subset <- data.frame(time, roll, pitch, head, temp, x_i, x_v, att_temp, amb_temp)
colnames(ts_subset) <- c('time', 'roll', 'pitch', 'heading', 'temp', 'xmit_i', 'xmit_v', 'attitude_T', 'ambient_T')
write.csv(ts_subset, paste(csv_data, adp_id, '_table_time_series', '.csv', sep=''), row.names=FALSE)

bin_subset <- data.frame(depth)
colnames(bin_subset) <- c('bin_depth')
write.csv(bin_subset, paste(csv_data, adp_id, '_table_bins', '.csv', sep=''), row.names=FALSE)

# ----
# Notes
########################################################################################
#### Loops to build tables individually for each of the subset tables ----
########################################################################################
#### 3d matrix data is accessed by dataframe[row, column, z-axis]
########################################################################################
#### Order of builds: average (x), beams 1-4
########################################################################################

# ----
########################################################################################
#### Amplitude tables
########################################################################################
# ---- ax
ampx <- data.frame()
for (i in 1:ln_prof) {
    a_avg <- rowMeans(a[i, 1:ln, c(1:4)])
    ampx <- rbind(ampx, a_avg)
}
amp_avg <- data.frame(time, ampx)
colnames(amp_avg) <- c('time',c(names))
write.csv(amp_avg, paste(csv_data, adp_id, '_amp_avg', '.csv', sep=''), row.names=FALSE)

# ---- a1
amp1 <- data.frame()
for (i in 1:ln_prof) {
    a1 <- ((a[i, 1:ln, 1]))
    amp1 <- rbind(amp1, a1)
}
amp_1 <- data.frame(time, amp1)
colnames(amp_1) <- c('time',c(names))
write.csv(amp_1, paste(csv_data, adp_id, '_amp_beam1', '.csv', sep=''), row.names=FALSE)

# ---- a2
amp2 <- data.frame()
for (i in 1:ln_prof) {
    a2 <- ((a[i, 1:ln, 2]))
    amp2 <- rbind(amp2, a2)
}
amp_2 <- data.frame(time, amp2)
colnames(amp_2) <- c('time',c(names))
write.csv(amp_2, paste(csv_data, adp_id, '_amp_beam2', '.csv', sep=''), row.names=FALSE)

# ---- a3
amp3 <- data.frame()
for (i in 1:ln_prof) {
    a3 <- ((a[i, 1:ln, 3]))
    amp3 <- rbind(amp3, a3)
}
amp_3 <- data.frame(time, amp3)
colnames(amp_3) <- c('time',c(names))
write.csv(amp_3, paste(csv_data, adp_id, '_amp_beam3', '.csv', sep=''), row.names=FALSE)

# ---- a4 
amp4 <- data.frame()
for (i in 1:ln_prof) {
    a4 <- ((a[i, 1:ln, 4]))
    amp4 <- rbind(amp4, a4)
}
amp_4 <- data.frame(time, amp4)
colnames(amp_4) <- c('time',c(names))
write.csv(amp_4, paste(csv_data, adp_id, '_amp_beam4', '.csv', sep=''), row.names=FALSE)

# ----
########################################################################################
#### Velocity tables
########################################################################################

# ---- v1
vel1 <- data.frame()
for (i in 1:ln_prof) {
    v1 <- ((v[i, 1:ln, 1]))
    vel1 <- rbind(vel1, v1)
}
vel_1 <- data.frame(time, vel1)
colnames(vel_1) <- c('time',c(names))
write.csv(vel_1, paste(csv_data, adp_id, '_vel_E_W', '.csv', sep=''), row.names=FALSE)

# ---- v2
vel2 <- data.frame()
for (i in 1:ln_prof) {
    v2 <- ((v[i, 1:ln, 2]))
    vel2 <- rbind(vel2, v2)
}
vel_2 <- data.frame(time, vel2)
colnames(vel_2) <- c('time',c(names))
write.csv(vel_2, paste(csv_data, adp_id, '_vel_N_S', '.csv', sep=''), row.names=FALSE)

# ---- v3
vel3 <- data.frame()
for (i in 1:ln_prof) {
    v3 <- ((v[i, 1:ln, 3]))
    vel3 <- rbind(vel3, v3)
}
vel_3 <- data.frame(time, vel3)
colnames(vel_3) <- c('time',c(names))
write.csv(vel_3, paste(csv_data, adp_id, '_vel_x_vrt', '.csv', sep=''), row.names=FALSE)

# ---- v4
vel4 <- data.frame()
for (i in 1:ln_prof) {
    v4 <- ((v[i, 1:ln, 4]))
    vel4 <- rbind(vel4, v4)
}
vel_4 <- data.frame(time, vel4)
colnames(vel_4) <- c('time',c(names))
write.csv(vel_4, paste(csv_data, adp_id, '_vel_err', '.csv', sep=''), row.names=FALSE)

# ----
########################################################################################
#### Quality/SNr tables
########################################################################################

# ----qx 
qualx <- data.frame()
for (i in 1:ln_prof) {
    qx <- rowMeans(q[i, 1:ln, c(1:4)])
    qualx <- rbind(qualx, qx)
}
corr_x <- data.frame(time, qualx)
colnames(corr_x) <- c('time',c(names))
write.csv(corr_x, paste(csv_data, adp_id, '_corr_avg', '.csv', sep=''), row.names=FALSE)

# ---- q1
qual1 <- data.frame()
for (i in 1:ln_prof) {
    q1 <- ((q[i, 1:ln, 1]))
    qual1 <- rbind(qual1, q1)
}
corr_1 <- data.frame(time, qual1)
colnames(corr_1) <- c('time',c(names))
write.csv(corr_1, paste(csv_data, adp_id, '_corr_bm1', '.csv', sep=''), row.names=FALSE)

# ---- q2 
qual2 <- data.frame()
for (i in 1:ln_prof) {
    q2 <- ((q[i, 1:ln, 2]))
    qual2 <- rbind(qual2, q2)
}
corr_2 <- data.frame(time, qual2)
colnames(corr_2) <- c('time',c(names))
write.csv(corr_2, paste(csv_data, adp_id, '_corr_bm2', '.csv', sep=''), row.names=FALSE)

# ---- q3 
qual3 <- data.frame()
for (i in 1:ln_prof) {
    q3 <- ((q[i, 1:ln, 3]))
    qual3 <- rbind(qual3, q3)
}
corr_3 <- data.frame(time, qual3)
colnames(corr_3) <- c('time',c(names))
write.csv(corr_3, paste(csv_data, adp_id, '_corr_bm3', '.csv', sep=''), row.names=FALSE)

# ---- q4 
qual4 <- data.frame()
for (i in 1:ln_prof) {
    q4 <- ((q[i, 1:ln, 4]))
    qual4 <- rbind(qual4, q4)
}
corr_4 <- data.frame(time, qual4)
colnames(corr_4) <- c('time',c(names))
write.csv(corr_4, paste(csv_data, adp_id, '_corr_bm4', '.csv', sep=''), row.names=FALSE)

# ----
########################################################################################
#### Goodness / % good tables
########################################################################################

# ---- gx 
goodx <- data.frame()
for (i in 1:ln_prof) {
    gx <- rowMeans(g[i, 1:ln, c(1:4)])
    goodx <- rbind(goodx, gx)
}
good_x <- data.frame(time, goodx)
colnames(good_x) <- c('time',c(names))
write.csv(good_x, paste(csv_data, adp_id, '_prcnt_good_avg', '.csv', sep=''), row.names=FALSE)

# ---- g1 
good1 <- data.frame()
for (i in 1:ln_prof) {
    g1 <- ((g[i, 1:ln, 1]))
    good1 <- rbind(good1, g1)
}
good_1 <- data.frame(time, good1)
colnames(good_1) <- c('time',c(names))
write.csv(good_1, paste(csv_data, adp_id, '_prcnt_good_bm1', '.csv', sep=''), row.names=FALSE)

# ---- g2 
good2 <- data.frame()
for (i in 1:ln_prof) {
    g2 <- ((g[i, 1:ln, 2]))
    good2 <- rbind(good2, g2)
}
good_2 <- data.frame(time, good2)
colnames(good_2) <- c('time',c(names))
write.csv(good_2, paste(csv_data, adp_id, '_prcnt_good_bm2', '.csv', sep=''), row.names=FALSE)

# ---- g3 
good3 <- data.frame()
for (i in 1:ln_prof) {
    g3 <- ((g[i, 1:ln, 3]))
    good3 <- rbind(good3, g3)
}
good_3 <- data.frame(time, good3)
colnames(good_3) <- c('time',c(names))
write.csv(good_3, paste(csv_data, adp_id, '_prcnt_good_bm3', '.csv', sep=''), row.names=FALSE)

# ---- g4
good4 <- data.frame()
for (i in 1:ln_prof) {
    g4 <- ((g[i, 1:ln, 4]))
    good4 <- rbind(good4, g4)
}
good_4 <- data.frame(time, good4)
colnames(good_4) <- c('time',c(names))
write.csv(good_4, paste(csv_data, adp_id, '_prcnt_good_bm4', '.csv', sep=''), row.names=FALSE)