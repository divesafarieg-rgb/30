def find_insert_position(arr, x):

    left, right = 0, len(arr)

    while left < right:
        mid = (left + right) // 2
        if arr[mid] < x:
            left = mid + 1
        else:
            right = mid

    return left