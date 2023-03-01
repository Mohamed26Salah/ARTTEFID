//
//  ARSCNMeshGeometry.swift
//  ScanningApp
//
//  Created by Mohamed Salah on 19/02/2023.
//  Copyright © 2023 Apple. All rights reserved.
//

import SceneKit
import ARKit
class ARSCNMeshGeometry {

    let scnGeometry: SCNGeometry
    
    var node: SCNNode {
        return SCNNode(geometry: scnGeometry)
    }
    
    init(meshAnchor: ARMeshAnchor) {
        let meshGeometry = meshAnchor.geometry
        
        // Vertices source
        let vertices = meshGeometry.vertices
        let verticesSource = SCNGeometrySource(buffer: vertices.buffer, vertexFormat: vertices.format, semantic: .vertex, vertexCount: vertices.count, dataOffset: vertices.offset, dataStride: vertices.stride)
     
        // Indices Element
        let faces = meshGeometry.faces
        let facesData = Data(bytesNoCopy: faces.buffer.contents(), count: faces.buffer.length, deallocator: .none)
        let facesElement = SCNGeometryElement(data: facesData, primitiveType: .triangles, primitiveCount: faces.count, bytesPerIndex: faces.bytesPerIndex)
        
        
        // Enabling this print statement causes the app to continue
//        print(faces.count)
        
        scnGeometry = SCNGeometry(sources: [verticesSource], elements: [facesElement])
    }
    
    func node(material: Any) -> SCNNode {
        let scnMaterial = SCNMaterial()
        scnMaterial.diffuse.contents = material
        
        let geometry = scnGeometry
        geometry.materials = [scnMaterial]
        return SCNNode(geometry: geometry)
    }
    

              

}
