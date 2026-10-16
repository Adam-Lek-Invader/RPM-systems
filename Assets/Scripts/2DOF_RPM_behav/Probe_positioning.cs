using UnityEngine;

[ExecuteAlways]
public class Probe_positioning : MonoBehaviour
{
    [Header("Loc from the center of Bee Chamber")]
    public float x = 0f;
    public float y = 0f;
    public float z = 0f;
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        this.transform.localPosition = new Vector3(x,y,z);
    }
}
