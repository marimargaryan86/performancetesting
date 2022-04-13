package gtfs

import (
    "fmt"
    "time"
)

func boolEncoder(v bool) ([]byte, error) {
    if v {
        return []byte("1"), nil
    }

    return []byte("0"), nil
}

func boolDecoder(data []byte, v *bool) error {
    if string(data) == "1" {
        *v = true
    } else {
        *v = false
    }

    return nil
}

func durationEncoder(v time.Duration) ([]byte, error) {
    minutes := int(v.Seconds()) / 60
    seconds := int(v.Seconds()) % 60
    hours := minutes / 60
    minutes = minutes % 60

    return []byte(fmt.Sprintf("%02d:%02d:%02d", hours, minutes, seconds)), nil
}

func durationDecoder(data []byte, v *time.Duration) error {
    var err error

    *v, err = time.ParseDuration(string(data))

    return err
}

func timeEncoder(v time.Time) ([]byte, error) {
    return []byte(v.Format("20060102")), nil
}

func timeDecoder(data []byte, v *time.Time) error {
    var err error

    *v, err = time.Parse("20060102", string(data))

    return err
}
