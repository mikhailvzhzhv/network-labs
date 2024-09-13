package main

import "time"

type Timer struct {
	sec       float64
	startTime time.Time
	partTime  time.Time
}

type SpeedChecker struct {
	timer          Timer
	bytesCount     int64
	partBytesCount int64
}

func (timer *Timer) init(sec float64) {
	timer.sec = sec
	timer.startTime = time.Now()
	timer.partTime = time.Now()
}

func (timer *Timer) expired() bool {
	return time.Since(timer.partTime).Seconds() > timer.sec
}

func (timer *Timer) reset() {
	timer.partTime = time.Now()
}

func (s *SpeedChecker) init(sec float64) {
	s.timer.init(sec)
	s.bytesCount = 0
	s.partBytesCount = 0
}

func (s *SpeedChecker) addData(count int64) {
	s.bytesCount += count
	s.partBytesCount += count
}

func (s *SpeedChecker) getAverageSpeed() int64 {
	return s.bytesCount / int64(time.Since(s.timer.startTime).Seconds())
}

func (s *SpeedChecker) getPartSpeed() int64 {
	return s.partBytesCount / int64(time.Since(s.timer.partTime).Seconds())
}

func (s *SpeedChecker) expired() bool {
	return s.timer.expired()
}

func (s *SpeedChecker) reset() {
	s.timer.reset()
	s.partBytesCount = 0
}
