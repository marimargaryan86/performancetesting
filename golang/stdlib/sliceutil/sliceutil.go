package sliceutil

func Equal[T comparable](a []T, b []T) bool {
	if len(a) != len(b) {
		return false
	}
	for i, v := range a {
		if v != b[i] {
			return false
		}
	}
	return true
}

func In[T comparable](a []T, b T) bool {
	for _, v := range a {
		if v == b {
			return true
		}
	}
	return false
}

func Map[T comparable, T2 comparable](input []T, callback func(T) T2) []T2 {
	output := make([]T2, len(input))
	for k, v := range input {
		output[k] = callback(v)
	}
	return output
}

func MostCommon[T comparable](slice []T) T {
	m := map[T]int{}
	var maxCnt int
	var freq T
	for _, a := range slice {
		m[a]++
		if m[a] > maxCnt {
			maxCnt = m[a]
			freq = a
		}
	}
	return freq
}

func Unique[T comparable](slice []T) []T {
	keys := make(map[T]struct{})
	list := make([]T, 0, len(slice))
	for _, entry := range slice {
		if _, value := keys[entry]; !value {
			keys[entry] = struct{}{}
			list = append(list, entry)
		}
	}
	return list
}

func Without[T comparable](slice []T, values ...T) []T {
	list := make([]T, 0, len(slice))
	for _, entry := range slice {
		if In(values, entry) {
			continue
		}
		list = append(list, entry)
	}
	return list
}
