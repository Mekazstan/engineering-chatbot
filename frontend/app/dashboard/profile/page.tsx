"use client"

import { useState } from "react"
import { Check, Copy, Edit, Key, Loader2, Save, User } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Separator } from "@/components/ui/separator"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"

export default function ProfilePage() {
  const [isEditing, setIsEditing] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [showApiKey, setShowApiKey] = useState(false)
  const [copied, setCopied] = useState(false)

  // User profile data
  const [profile, setProfile] = useState({
    name: "John Doe",
    email: "john@example.com",
    company: "Acme Inc.",
    jobTitle: "Field Engineer",
    phone: "+1 (555) 123-4567",
    apiKey: "sk_live_TechAssist_51a2c98e7f83e2a0b408",
  })

  // Email preferences
  const [emailPreferences, setEmailPreferences] = useState({
    updates: true,
    tips: true,
    security: true,
    newsletter: false,
  })

  // Usage statistics
  const usage = {
    queries: {
      current: 28,
      limit: 50,
      percentage: 56,
    },
    documents: {
      current: 3,
      limit: 3,
      percentage: 100,
    },
    plan: "Free",
    renewalDate: new Date(2025, 3, 15),
  }

  const handleSaveProfile = () => {
    setIsSaving(true)

    // Simulate API call
    setTimeout(() => {
      setIsSaving(false)
      setIsEditing(false)
    }, 1000)
  }

  const copyApiKey = () => {
    navigator.clipboard.writeText(profile.apiKey)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const regenerateApiKey = () => {
    // Simulate API key regeneration
    setProfile({
      ...profile,
      apiKey: "sk_live_TechAssist_" + Math.random().toString(36).substring(2, 15),
    })
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Profile</h2>
        <p className="text-muted-foreground">Manage your account settings and preferences</p>
      </div>

      <Tabs defaultValue="general" className="space-y-4">
        <TabsList>
          <TabsTrigger value="general">General</TabsTrigger>
          <TabsTrigger value="preferences">Preferences</TabsTrigger>
          <TabsTrigger value="subscription">Subscription</TabsTrigger>
          <TabsTrigger value="api">API</TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="space-y-4">
          <Card>
            <CardHeader className="space-y-1">
              <div className="flex items-center justify-between">
                <CardTitle className="text-2xl">Personal Information</CardTitle>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => (isEditing ? handleSaveProfile() : setIsEditing(true))}
                  disabled={isSaving}
                >
                  {isSaving ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Saving
                    </>
                  ) : isEditing ? (
                    <>
                      <Save className="mr-2 h-4 w-4" />
                      Save
                    </>
                  ) : (
                    <>
                      <Edit className="mr-2 h-4 w-4" />
                      Edit
                    </>
                  )}
                </Button>
              </div>
              <CardDescription>Update your personal information and contact details</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex flex-col md:flex-row gap-6">
                <div className="flex flex-col items-center gap-4">
                  <Avatar className="h-24 w-24">
                    <AvatarImage src="/placeholder.svg?height=96&width=96" alt={profile.name} />
                    <AvatarFallback className="text-2xl">
                      {profile.name
                        .split(" ")
                        .map((n) => n[0])
                        .join("")}
                    </AvatarFallback>
                  </Avatar>
                  {isEditing && (
                    <Button variant="outline" size="sm">
                      Change Avatar
                    </Button>
                  )}
                </div>
                <div className="flex-1 space-y-4">
                  <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                    <div className="space-y-2">
                      <Label htmlFor="name">Full Name</Label>
                      <Input
                        id="name"
                        value={profile.name}
                        onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                        disabled={!isEditing}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="email">Email</Label>
                      <Input
                        id="email"
                        type="email"
                        value={profile.email}
                        onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                        disabled={!isEditing}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="company">Company</Label>
                      <Input
                        id="company"
                        value={profile.company}
                        onChange={(e) => setProfile({ ...profile, company: e.target.value })}
                        disabled={!isEditing}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="jobTitle">Job Title</Label>
                      <Input
                        id="jobTitle"
                        value={profile.jobTitle}
                        onChange={(e) => setProfile({ ...profile, jobTitle: e.target.value })}
                        disabled={!isEditing}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="phone">Phone Number</Label>
                      <Input
                        id="phone"
                        value={profile.phone}
                        onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                        disabled={!isEditing}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Security</CardTitle>
              <CardDescription>Manage your password and security settings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="current-password">Current Password</Label>
                <Input id="current-password" type="password" disabled={!isEditing} />
              </div>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="new-password">New Password</Label>
                  <Input id="new-password" type="password" disabled={!isEditing} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="confirm-password">Confirm New Password</Label>
                  <Input id="confirm-password" type="password" disabled={!isEditing} />
                </div>
              </div>
            </CardContent>
            <CardFooter>
              <Button variant="outline" disabled={!isEditing}>
                Change Password
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>

        <TabsContent value="preferences" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Email Preferences</CardTitle>
              <CardDescription>Manage how and when you receive email notifications</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="updates">Product Updates</Label>
                    <p className="text-sm text-muted-foreground">Receive emails about new features and improvements</p>
                  </div>
                  <Switch
                    id="updates"
                    checked={emailPreferences.updates}
                    onCheckedChange={(checked) => setEmailPreferences({ ...emailPreferences, updates: checked })}
                  />
                </div>
                <Separator />
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="tips">Tips & Tutorials</Label>
                    <p className="text-sm text-muted-foreground">
                      Get helpful tips on how to use TechAssist AI effectively
                    </p>
                  </div>
                  <Switch
                    id="tips"
                    checked={emailPreferences.tips}
                    onCheckedChange={(checked) => setEmailPreferences({ ...emailPreferences, tips: checked })}
                  />
                </div>
                <Separator />
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="security">Security Alerts</Label>
                    <p className="text-sm text-muted-foreground">Important notifications about your account security</p>
                  </div>
                  <Switch
                    id="security"
                    checked={emailPreferences.security}
                    onCheckedChange={(checked) => setEmailPreferences({ ...emailPreferences, security: checked })}
                  />
                </div>
                <Separator />
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="newsletter">Newsletter</Label>
                    <p className="text-sm text-muted-foreground">Monthly newsletter with industry insights and news</p>
                  </div>
                  <Switch
                    id="newsletter"
                    checked={emailPreferences.newsletter}
                    onCheckedChange={(checked) => setEmailPreferences({ ...emailPreferences, newsletter: checked })}
                  />
                </div>
              </div>
            </CardContent>
            <CardFooter>
              <Button>Save Preferences</Button>
            </CardFooter>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Application Preferences</CardTitle>
              <CardDescription>Customize your experience with TechAssist AI</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="dark-mode">Dark Mode</Label>
                    <p className="text-sm text-muted-foreground">Switch between light and dark theme</p>
                  </div>
                  <Switch id="dark-mode" />
                </div>
                <Separator />
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="auto-save">Auto-Save Chats</Label>
                    <p className="text-sm text-muted-foreground">Automatically save your chat history</p>
                  </div>
                  <Switch id="auto-save" defaultChecked />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="subscription" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Current Plan</CardTitle>
                <Badge variant={usage.plan === "Free" ? "secondary" : "default"}>{usage.plan}</Badge>
              </div>
              <CardDescription>Your current subscription plan and usage</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Monthly Queries</span>
                  <span className="text-sm font-medium">
                    {usage.queries.current}/{usage.queries.limit}
                  </span>
                </div>
                <div className="h-2 w-full rounded-full bg-muted">
                  <div className="h-full rounded-full bg-primary" style={{ width: `${usage.queries.percentage}%` }} />
                </div>
                <p className="text-xs text-muted-foreground">{usage.queries.percentage}% of monthly query quota used</p>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Document Storage</span>
                  <span className="text-sm font-medium">
                    {usage.documents.current}/{usage.documents.limit}
                  </span>
                </div>
                <div className="h-2 w-full rounded-full bg-muted">
                  <div className="h-full rounded-full bg-primary" style={{ width: `${usage.documents.percentage}%` }} />
                </div>
                <p className="text-xs text-muted-foreground">{usage.documents.percentage}% of document storage used</p>
              </div>

              <div className="rounded-lg border p-4">
                <div className="flex flex-col gap-2">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">Plan Renewal</span>
                    <span>{usage.renewalDate.toLocaleDateString()}</span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Your {usage.plan} plan will renew automatically on {usage.renewalDate.toLocaleDateString()}.
                  </p>
                </div>
              </div>
            </CardContent>
            <CardFooter className="flex flex-col items-start gap-2">
              <div className="text-sm text-muted-foreground mb-2">
                Upgrade to Pro for unlimited queries and document storage.
              </div>
              <Button>Upgrade to Pro</Button>
            </CardFooter>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Billing History</CardTitle>
              <CardDescription>View your past invoices and payment history</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {usage.plan === "Free" ? (
                  <Alert>
                    <User className="h-4 w-4" />
                    <AlertTitle>Free Plan</AlertTitle>
                    <AlertDescription>
                      You are currently on the free plan. No billing history available.
                    </AlertDescription>
                  </Alert>
                ) : (
                  <div className="rounded-md border">
                    <div className="flex items-center justify-between p-4">
                      <div>
                        <div className="font-medium">Pro Plan - Monthly</div>
                        <div className="text-sm text-muted-foreground">March 15, 2025</div>
                      </div>
                      <div className="text-right">
                        <div className="font-medium">$29.00</div>
                        <div className="text-sm text-green-600">Paid</div>
                      </div>
                    </div>
                    <Separator />
                    <div className="flex items-center justify-between p-4">
                      <div>
                        <div className="font-medium">Pro Plan - Monthly</div>
                        <div className="text-sm text-muted-foreground">February 15, 2025</div>
                      </div>
                      <div className="text-right">
                        <div className="font-medium">$29.00</div>
                        <div className="text-sm text-green-600">Paid</div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="api" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>API Access</CardTitle>
              <CardDescription>Manage your API keys for programmatic access to TechAssist AI</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Alert>
                <Key className="h-4 w-4" />
                <AlertTitle>API Access</AlertTitle>
                <AlertDescription>
                  Your API key grants full access to your TechAssist AI account. Keep it secure and never share it
                  publicly.
                </AlertDescription>
              </Alert>

              <div className="space-y-2">
                <Label htmlFor="api-key">API Key</Label>
                <div className="flex">
                  <Input
                    id="api-key"
                    value={showApiKey ? profile.apiKey : "•".repeat(profile.apiKey.length)}
                    readOnly
                    className="font-mono text-sm rounded-r-none"
                  />
                  <Button
                    variant="outline"
                    className="rounded-l-none border-l-0"
                    onClick={() => setShowApiKey(!showApiKey)}
                  >
                    {showApiKey ? "Hide" : "Show"}
                  </Button>
                  <Button variant="outline" className="ml-2" onClick={copyApiKey}>
                    {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                    <span className="ml-2">{copied ? "Copied" : "Copy"}</span>
                  </Button>
                </div>
              </div>

              <div className="pt-4">
                <Button variant="outline" onClick={regenerateApiKey}>
                  Regenerate API Key
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>API Documentation</CardTitle>
              <CardDescription>Resources to help you integrate with our API</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="rounded-lg border p-4">
                  <h3 className="font-medium mb-2">Getting Started</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Learn how to make your first API request and authenticate.
                  </p>
                  <Button variant="outline" size="sm">
                    View Guide
                  </Button>
                </div>
                <div className="rounded-lg border p-4">
                  <h3 className="font-medium mb-2">API Reference</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Complete documentation of all available endpoints.
                  </p>
                  <Button variant="outline" size="sm">
                    View Reference
                  </Button>
                </div>
                <div className="rounded-lg border p-4">
                  <h3 className="font-medium mb-2">Code Examples</h3>
                  <p className="text-sm text-muted-foreground mb-4">Sample code in various programming languages.</p>
                  <Button variant="outline" size="sm">
                    View Examples
                  </Button>
                </div>
                <div className="rounded-lg border p-4">
                  <h3 className="font-medium mb-2">Rate Limits</h3>
                  <p className="text-sm text-muted-foreground mb-4">Understanding API rate limits and quotas.</p>
                  <Button variant="outline" size="sm">
                    View Limits
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

